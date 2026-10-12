#!/usr/bin/env python3

import curses
import json
import time

FILE = "status.json"
REFRESH_SECONDS = 1.0
COL_WIDTH = 58
GAP = 3


def format_time(seconds):
    if seconds is None:
        return "-"
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes}:{seconds:02d}"


def format_value(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def load_data():
    try:
        with open(FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def row_text(r):
    return (
        f"{r.get('state', '-')[:10]:<10} "
        f"{r.get('seed', '-'):>4} "
        f"{r.get('family', '-')[:5]:<5} "
        f"{r.get('status', '-')[:7]:<7} "
        f"{format_time(r.get('wall_seconds')):>7} "
        f"{format_value(r.get('cat')):>8} "
        f"{format_value(r.get('reg')):>8}"
    )


def safe_addstr(stdscr, y, x, text, attr=0):
    h, w = stdscr.getmaxyx()

    if not (0 <= y < h and 0 <= x < w):
        return

    try:
        stdscr.addnstr(y, x, text, max(0, w - x - 1), attr)
    except curses.error:
        pass


def prompt_search(stdscr):
    h, w = stdscr.getmaxyx()

    curses.echo()
    curses.curs_set(1)

    prompt = "State search: "
    safe_addstr(
        stdscr,
        h - 1,
        0,
        prompt + " " * max(0, w - len(prompt) - 1),
        curses.A_REVERSE,
    )

    stdscr.timeout(-1)

    try:
        stdscr.move(h - 1, len(prompt))
        value = stdscr.getstr(h - 1, len(prompt), 30).decode().strip()
    except Exception:
        value = ""

    stdscr.timeout(50)
    curses.noecho()
    curses.curs_set(0)

    return value


def main(stdscr):
    curses.curs_set(0)
    curses.noecho()
    stdscr.keypad(True)

    # Wait at most 50 ms for input.
    # Much more responsive than nodelay + sleep.
    stdscr.timeout(50)

    scroll = 0
    search = ""

    data = None
    last_load = 0.0

    while True:
        now = time.monotonic()

        if data is None or now - last_load >= REFRESH_SECONDS:
            new_data = load_data()
            if new_data is not None:
                data = new_data
            last_load = now

        if data is None:
            stdscr.erase()
            safe_addstr(stdscr, 0, 0, "Unable to read status.json")
            stdscr.refresh()

            key = stdscr.getch()
            if key in (ord("q"), ord("Q")):
                break

            continue

        h, w = stdscr.getmaxyx()

        cells = data.get("cells", [])

        if search:
            query = search.lower()
            cells = [
                r for r in cells
                if query in str(r.get("state", "")).lower()
            ]

        start_y = 4

        # Reserve:
        # 3 metadata rows
        # 1 table header
        # 1 bottom status row
        visible_rows = max(1, h - start_y - 2)

        two_columns = w >= (COL_WIDTH * 2 + GAP)

        #
        # SCROLL IS A PHYSICAL SCREEN ROW.
        #
        # Two-column layout:
        #
        # left              right
        # cells[0]          cells[N]
        # cells[1]          cells[N+1]
        # ...
        #
        # Scrolling down one line gives:
        #
        # cells[1]          cells[N+1]
        # cells[2]          cells[N+2]
        #
        # No re-splitting, so entries never duplicate/reorder.
        #

        if two_columns:
            capacity = visible_rows * 2
            max_scroll = max(0, len(cells) - capacity)
        else:
            capacity = visible_rows
            max_scroll = max(0, len(cells) - capacity)

        scroll = max(0, min(scroll, max_scroll))

        stdscr.erase()

        updated = data.get("updated_at", "-")
        phase = data.get("phase", "-")
        gpu = data.get("gpu_free_mib", "-")
        disk = data.get("disk_free_gb", "-")
        home = data.get("disk_free_gb_home", "-")

        safe_addstr(
            stdscr,
            0,
            0,
            f"Phase: {phase} | GPU: {gpu} MiB | Disk: {disk} GB | Home: {home} GB",
            curses.A_BOLD,
        )

        safe_addstr(
            stdscr,
            1,
            0,
            f"Updated: {updated}",
        )

        filter_text = search or "ALL"

        safe_addstr(
            stdscr,
            2,
            0,
            (
                f"State: {filter_text} | Rows: {len(cells)} | "
                f"↑↓/jk scroll | PgUp/PgDn | / search | c clear | q quit"
            ),
            curses.A_REVERSE,
        )

        header = (
            f"{'STATE':<10} "
            f"{'SEED':>4} "
            f"{'FAM':<5} "
            f"{'STATUS':<7} "
            f"{'TIME':>7} "
            f"{'CAT':>8} "
            f"{'REG':>8}"
        )

        safe_addstr(stdscr, start_y, 0, header, curses.A_BOLD)

        if two_columns:
            right_x = COL_WIDTH + GAP
            safe_addstr(
                stdscr,
                start_y,
                right_x,
                header,
                curses.A_BOLD,
            )

            for screen_row in range(visible_rows):
                y = start_y + 1 + screen_row

                left_index = scroll + screen_row
                right_index = scroll + visible_rows + screen_row

                if left_index < len(cells):
                    r = cells[left_index]

                    attr = 0
                    if r.get("status") == "running":
                        attr |= curses.A_BOLD

                    safe_addstr(
                        stdscr,
                        y,
                        0,
                        row_text(r),
                        attr,
                    )

                if right_index < len(cells):
                    r = cells[right_index]

                    attr = 0
                    if r.get("status") == "running":
                        attr |= curses.A_BOLD

                    safe_addstr(
                        stdscr,
                        y,
                        right_x,
                        row_text(r),
                        attr,
                    )

        else:
            for screen_row in range(visible_rows):
                index = scroll + screen_row

                if index >= len(cells):
                    break

                r = cells[index]

                attr = 0
                if r.get("status") == "running":
                    attr |= curses.A_BOLD

                safe_addstr(
                    stdscr,
                    start_y + 1 + screen_row,
                    0,
                    row_text(r),
                    attr,
                )

        running = data.get("running", [])

        if running:
            running_text = "RUNNING: " + " | ".join(
                (
                    f"{r.get('state')} "
                    f"s={r.get('seed')} "
                    f"{r.get('family')} "
                    f"pid={r.get('pid')}"
                )
                for r in running
            )
        else:
            running_text = "RUNNING: none"

        safe_addstr(
            stdscr,
            h - 1,
            0,
            running_text,
            curses.A_BOLD,
        )

        stdscr.refresh()

        key = stdscr.getch()

        if key == -1:
            continue

        if key in (ord("q"), ord("Q")):
            break

        # Arrow down OR vim j
        elif key in (curses.KEY_DOWN, ord("j"), ord("J")):
            scroll = min(max_scroll, scroll + 1)

        # Arrow up OR vim k
        elif key in (curses.KEY_UP, ord("k"), ord("K")):
            scroll = max(0, scroll - 1)

        elif key == curses.KEY_NPAGE:
            scroll = min(
                max_scroll,
                scroll + visible_rows,
            )

        elif key == curses.KEY_PPAGE:
            scroll = max(
                0,
                scroll - visible_rows,
            )

        elif key == curses.KEY_HOME:
            scroll = 0

        elif key == curses.KEY_END:
            scroll = max_scroll

        elif key == ord("/"):
            search = prompt_search(stdscr)
            scroll = 0

        elif key in (ord("c"), ord("C")):
            search = ""
            scroll = 0


if __name__ == "__main__":
    curses.wrapper(main)
