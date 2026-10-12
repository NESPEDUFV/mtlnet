"""AUT-35a instrument: read a remote ZIP's central directory over HTTP ranges,
then stream-inflate the head of one chosen member.

Purpose: establish, first-hand, the SCHEMA and the earliest timestamps of
Yelp's checkin.json without downloading 4.35 GB.

Usage:
  python3 _tmp_zipprobe.py <url> list
  python3 _tmp_zipprobe.py <url> head <member-substring> <bytes>
"""
import sys
import re
import struct
import zlib
import subprocess

url = sys.argv[1]
mode = sys.argv[2]


def rng(a, b):
    out = subprocess.run(
        ["curl", "-sSL", "-m", "600", "-r", str(a) + "-" + str(b), url],
        capture_output=True, check=True)
    return out.stdout, None


def total():
    out = subprocess.run(["curl", "-sSLI", "-m", "120", url],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    cl = re.findall(r"(?im)^content-length:\s*(\d+)", out)
    lm = re.findall(r"(?im)^last-modified:\s*(.+)$", out)
    return int(cl[-1]), (lm[-1].strip() if lm else None)


size, lastmod = total()
print("REMOTE size=" + str(size) + " last_modified=" + str(lastmod))

tail, _ = rng(max(0, size - 200000), size - 1)
# ZIP64 end of central directory locator
i = tail.rfind(b"PK\x06\x07")
j = tail.rfind(b"PK\x06\x05")
if i != -1:
    cd_off_of_z64eocd = struct.unpack("<Q", tail[i + 8:i + 16])[0]
    z64, _ = rng(cd_off_of_z64eocd, cd_off_of_z64eocd + 55)
    cd_size = struct.unpack("<Q", z64[40:48])[0]
    cd_off = struct.unpack("<Q", z64[48:56])[0]
    print("ZIP64 central_dir offset=" + str(cd_off) + " size=" + str(cd_size))
else:
    cd_size = struct.unpack("<I", tail[j + 12:j + 16])[0]
    cd_off = struct.unpack("<I", tail[j + 16:j + 20])[0]
    print("ZIP central_dir offset=" + str(cd_off) + " size=" + str(cd_size))

cd, _ = rng(cd_off, cd_off + cd_size - 1)
entries = []
p = 0
while p < len(cd) - 4 and cd[p:p + 4] == b"PK\x01\x02":
    method = struct.unpack("<H", cd[p + 10:p + 12])[0]
    csize = struct.unpack("<I", cd[p + 20:p + 24])[0]
    usize = struct.unpack("<I", cd[p + 24:p + 28])[0]
    nlen = struct.unpack("<H", cd[p + 28:p + 30])[0]
    elen = struct.unpack("<H", cd[p + 30:p + 32])[0]
    clen = struct.unpack("<H", cd[p + 32:p + 34])[0]
    lho = struct.unpack("<I", cd[p + 42:p + 46])[0]
    name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
    extra = cd[p + 46 + nlen:p + 46 + nlen + elen]
    # ZIP64 extra field 0x0001
    q = 0
    while q + 4 <= len(extra):
        hid, hsz = struct.unpack("<HH", extra[q:q + 4])
        if hid == 1:
            vals = extra[q + 4:q + 4 + hsz]
            k = 0
            if usize == 0xFFFFFFFF and k + 8 <= len(vals):
                usize = struct.unpack("<Q", vals[k:k + 8])[0]
                k += 8
            if csize == 0xFFFFFFFF and k + 8 <= len(vals):
                csize = struct.unpack("<Q", vals[k:k + 8])[0]
                k += 8
            if lho == 0xFFFFFFFF and k + 8 <= len(vals):
                lho = struct.unpack("<Q", vals[k:k + 8])[0]
                k += 8
        q += 4 + hsz
    entries.append((name, method, csize, usize, lho))
    p += 46 + nlen + elen + clen

for e in entries:
    print("ENTRY name=" + e[0] + " method=" + str(e[1]) + " csize=" + str(e[2]) + " usize=" + str(e[3]) + " lho=" + str(e[4]))

if mode == "head":
    want = sys.argv[3]
    nbytes = int(sys.argv[4])
    hit = [e for e in entries if want in e[0]]
    print("MATCHES=" + repr([h[0] for h in hit]))
    name, method, csize, usize, lho = hit[0]
    lh, _ = rng(lho, lho + 29)
    nlen = struct.unpack("<H", lh[26:28])[0]
    elen = struct.unpack("<H", lh[28:30])[0]
    data_off = lho + 30 + nlen + elen
    grab = min(csize, 6 * 1024 * 1024)
    blob, _ = rng(data_off, data_off + grab - 1)
    if method == 8:
        d = zlib.decompressobj(-zlib.MAX_WBITS)
    else:
        d = None
    out = d.decompress(blob, nbytes) if d else blob[:nbytes]
    txt = out.decode("utf-8", "replace")
    print("=== HEAD of " + name + " (" + str(len(out)) + " bytes of " + str(usize) + ") ===")
    print(txt[:nbytes])
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", txt)
    print("=== date-like tokens found: " + str(len(dates)) + " ; min=" + (min(dates) if dates else "-") + " max=" + (max(dates) if dates else "-"))
    yrs = sorted(set(x[:4] for x in dates))
    print("=== years present in this head sample: " + repr(yrs))
