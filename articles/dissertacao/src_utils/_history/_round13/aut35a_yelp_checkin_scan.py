"""AUT-35a instrument: stream-inflate the yelp_dataset.tar member of the Yelp
Open Dataset zip and report the MAX timestamp in checkin.json, without storing
the 4.34 GB payload.

Bounded: stops after CAP bytes of inflated tar. Prints every tar member header
it passes, so a "not reached" outcome is distinguishable from "absent".
"""
import subprocess
import zlib
import re
import sys

URL = "https://business.yelp.com/external-assets/files/Yelp-JSON.zip"
DATA_OFF = 115035 + 30 + 22 + 32  # local header at 115035; refined below
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 3_000_000_000

# resolve the true data offset from the local file header
lh = subprocess.run(["curl", "-sSL", "-m", "120", "-r", "115035-115064", URL],
                    capture_output=True, check=True).stdout
import struct
nlen = struct.unpack("<H", lh[26:28])[0]
elen = struct.unpack("<H", lh[28:30])[0]
DATA_OFF = 115035 + 30 + nlen + elen
print("tar member data offset=" + str(DATA_OFF))

p = subprocess.Popen(["curl", "-sSL", "-m", "5400", "-r", str(DATA_OFF) + "-", URL],
                     stdout=subprocess.PIPE)
# Two-stage: the zip member is DEFLATE, and the payload it yields is itself a
# GZIP stream (magic 1f 8b) despite the ".tar" filename. Verified 2026-08-04 by
# dumping the first 512 inflated bytes. A single-stage decompressor desyncs the
# tar header walk silently, which is exactly the V3 blindness this note records.
_d1 = zlib.decompressobj(-zlib.MAX_WBITS)
_d2 = zlib.decompressobj(16 + zlib.MAX_WBITS)


class Chain:
    def decompress(self, b):
        return _d2.decompress(_d1.decompress(b))


dec = Chain()

buf = b""
pos = 0            # position in the inflated tar stream
consumed = 0
in_checkin = False
checkin_remaining = 0
maxdate = None
mindate = None
years = {}
tail = b""
DATE = re.compile(rb"\d{4}-\d{2}-\d{2}")

while consumed < CAP:
    chunk = p.stdout.read(1 << 20)
    if not chunk:
        break
    data = dec.decompress(chunk)
    if not data:
        continue
    consumed += len(data)
    buf += data

    while True:
        if in_checkin:
            take = min(len(buf), checkin_remaining)
            seg = tail + buf[:take]
            for m in DATE.finditer(seg):
                d = m.group(0).decode()
                years[d[:4]] = years.get(d[:4], 0) + 1
                if maxdate is None or d > maxdate:
                    maxdate = d
                if mindate is None or d < mindate:
                    mindate = d
            tail = seg[-32:]
            buf = buf[take:]
            checkin_remaining -= take
            if checkin_remaining == 0:
                in_checkin = False
                print("CHECKIN DONE min=" + str(mindate) + " max=" + str(maxdate))
                print("YEARS=" + repr(sorted(years.items())))
                p.kill()
                sys.exit(0)
            if not buf:
                break
        else:
            if len(buf) < 512:
                break
            hdr = buf[:512]
            name = hdr[:100].rstrip(b"\x00").decode("utf-8", "replace")
            if not name:
                buf = buf[512:]
                continue
            szf = hdr[124:136].rstrip(b"\x00 ").decode("ascii", "replace")
            try:
                sz = int(szf, 8) if szf else 0
            except ValueError:
                sz = 0
            print("TAR member=" + name + " size=" + str(sz) + " at_inflated=" + str(consumed))
            buf = buf[512:]
            if "checkin" in name.lower():
                in_checkin = True
                checkin_remaining = sz
                tail = b""
            else:
                skip = (sz + 511) // 512 * 512
                if len(buf) >= skip:
                    buf = buf[skip:]
                else:
                    # need to stream past this member
                    need = skip - len(buf)
                    buf = b""
                    while need > 0 and consumed < CAP:
                        c = p.stdout.read(1 << 20)
                        if not c:
                            break
                        dd = dec.decompress(c)
                        consumed += len(dd)
                        if len(dd) <= need:
                            need -= len(dd)
                        else:
                            buf = dd[need:]
                            need = 0
                    if need > 0:
                        print("CAP or EOF reached while skipping " + name)
                        p.kill()
                        sys.exit(2)
print("CAP/EOF reached without completing checkin.json; inflated=" + str(consumed))
p.kill()
sys.exit(3)
