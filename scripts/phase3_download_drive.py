#!/usr/bin/env python3
"""Phase 3 Drive downloader.

Lists folder contents via gdown's `skip_download=True` path (which works), then
downloads each file via a direct `requests` session that handles the
confirm-token interstitial Drive shows for files larger than ~100 MB. This
sidesteps gdown 6.0's broken downloader code path on this network.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

import gdown
import requests

DRIVE_FILE_URL = "https://drive.usercontent.google.com/download"
CHUNK_SIZE = 4 * 1024 * 1024  # 4 MiB


class _FormParser(HTMLParser):
    """Pull <form action> + <input name/value> pairs out of Drive's confirm page."""

    def __init__(self) -> None:
        super().__init__()
        self.action: str | None = None
        self.fields: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "form" and self.action is None:
            self.action = a.get("action")
        elif tag == "input":
            name = a.get("name")
            if name:
                self.fields[name] = a.get("value", "") or ""


def _parse_confirm_form(html: str) -> tuple[str, dict[str, str]] | None:
    p = _FormParser()
    p.feed(html)
    if p.action and "confirm" in p.fields:
        return p.action, p.fields
    return None


def download_one(
    file_id: str,
    out_path: Path,
    session: requests.Session,
    *,
    max_retries: int = 3,
) -> tuple[str, str, int]:
    """Download a single file. Returns (file_id, status, bytes)."""
    if out_path.exists() and out_path.stat().st_size > 0:
        return (file_id, "skipped", out_path.stat().st_size)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")

    last_err: str | None = None
    for attempt in range(1, max_retries + 1):
        try:
            params = {"id": file_id, "export": "download"}
            r = session.get(DRIVE_FILE_URL, params=params, stream=True, timeout=60)
            r.raise_for_status()

            ctype = r.headers.get("content-type", "")
            if ctype.startswith("text/html"):
                # Confirm interstitial — parse form, follow it.
                form = _parse_confirm_form(r.text)
                if form is None:
                    snippet = r.text[:300].replace("\n", " ")
                    raise RuntimeError(f"unexpected HTML response: {snippet}")
                action, fields = form
                r = session.get(action, params=fields, stream=True, timeout=60)
                r.raise_for_status()
                ctype = r.headers.get("content-type", "")
                if ctype.startswith("text/html"):
                    snippet = r.text[:300].replace("\n", " ")
                    raise RuntimeError(f"still got HTML after confirm: {snippet}")

            total = 0
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)

            if total == 0:
                raise RuntimeError("empty download")

            tmp_path.replace(out_path)
            return (file_id, "ok", total)

        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            tmp_path.unlink(missing_ok=True)
            if attempt < max_retries:
                time.sleep(2 * attempt)
            continue

    return (file_id, f"FAIL: {last_err}", 0)


def list_folder(folder_url: str, output_root: Path) -> list:
    """Return gdown's GoogleDriveFileToDownload list for a folder."""
    return gdown.download_folder(
        url=folder_url,
        output=str(output_root) + "/",
        quiet=True,
        skip_download=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", action="append", required=True,
                    help="Drive folder URL (can be repeated)")
    ap.add_argument("--output", required=True, help="Local root directory")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--exclude", action="append", default=[],
                    help="Skip any file whose relative path starts with this prefix")
    args = ap.parse_args()

    output_root = Path(args.output).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    all_files = []
    for url in args.folder:
        print(f"[list] {url}", flush=True)
        items = list_folder(url, output_root)
        print(f"       got {len(items)} files", flush=True)
        all_files.extend(items)

    # Filter
    if args.exclude:
        before = len(all_files)
        all_files = [
            f for f in all_files
            if not any(Path(f.path).parts and Path(f.path).parts[0] == ex
                       for ex in args.exclude)
        ]
        print(f"[filter] {before} -> {len(all_files)} (excluded "
              f"{', '.join(args.exclude)})", flush=True)

    # Download in parallel
    print(f"[download] {len(all_files)} files, {args.workers} workers", flush=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 phase3-fetch"})

    ok = skipped = failed = 0
    fail_list: list[tuple[str, str]] = []
    total_bytes = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {
            ex.submit(download_one, f.id, Path(f.local_path), session): f
            for f in all_files
        }
        for i, fut in enumerate(as_completed(futures), 1):
            f = futures[fut]
            fid, status, nbytes = fut.result()
            if status == "ok":
                ok += 1
                total_bytes += nbytes
                print(f"  [{i:3d}/{len(all_files)}] ok      "
                      f"{nbytes/1024/1024:7.2f} MiB  {f.path}", flush=True)
            elif status == "skipped":
                skipped += 1
                if i % 20 == 0:
                    print(f"  [{i:3d}/{len(all_files)}] skipped {f.path}", flush=True)
            else:
                failed += 1
                fail_list.append((f.path, status))
                print(f"  [{i:3d}/{len(all_files)}] FAIL    {f.path}  ({status})",
                      flush=True)

    dt = time.time() - t0
    print(f"\n[summary] ok={ok} skipped={skipped} failed={failed}  "
          f"total={total_bytes/1024/1024:.1f} MiB in {dt:.1f}s", flush=True)
    if fail_list:
        print("\n[failures]", flush=True)
        for path, err in fail_list:
            print(f"  {path}\n    -> {err}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
