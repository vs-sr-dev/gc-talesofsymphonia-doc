"""Read the `.cab` archives on the GameCube discs.

Forty-five files on each disc begin with `MSCF`, the signature of a Microsoft
Cabinet.  They are not cabinets.  The header is well formed -- signature,
sizes, one folder, one file, a name and a length -- but the folder claims zero
data blocks and no compression while the payload is a third the size the file
entry declares, so nothing that reads cabinets could unpack one.  What the
format is being used for is its *file entry*: a name, an uncompressed length,
and an MS-DOS date and time.

That makes these the only per-asset timestamps on either release, and they are
the reason this file exists.  They date the assets rather than the disc, so
they show the order the pipeline ran in -- and they show which assets stopped
being rebuilt.

    python tools/cab.py --gc  DISC.gcm [DISC2.gcm] [--sorted]
    python tools/cab.py --cvm FILE.CVM [FILE.CVM ...] [--sorted]
    python tools/cab.py FILE.cab
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcm
import cvm


def dos_stamp(date, time):
    y = ((date >> 9) & 0x7F) + 1980
    mo = (date >> 5) & 0x0F
    d = date & 0x1F
    h = (time >> 11) & 0x1F
    mi = (time >> 5) & 0x3F
    s = (time & 0x1F) * 2
    return '%04d-%02d-%02d %02d:%02d:%02d' % (y, mo, d, h, mi, s)


def parse(buf):
    """(header fields, [(name, size, stamp, attribs)])"""
    if buf[:4] != b'MSCF':
        return None, []
    (csize, coff, vmin, vmaj, nfold, nfiles,
     flags) = struct.unpack_from('<I4xI4xBBHHH', buf, 8)
    folders = []
    o = 36
    for _ in range(nfold):
        folders.append(struct.unpack_from('<IHH', buf, o))
        o += 8
    files = []
    o = coff
    for _ in range(nfiles):
        if o + 17 > len(buf):
            break
        size, fo, fi, date, time, at = struct.unpack_from('<IIHHHH', buf, o)
        e = buf.find(b'\0', o + 16)
        if e < 0:
            break
        name = buf[o + 16:e].decode('cp932', 'replace')
        files.append((name, size, dos_stamp(date, time), at, fi, coff, e + 1))
        o = e + 1
    head = dict(cab_size=csize, first_file=coff,
                version='%d.%d' % (vmaj, vmin), folders=folders,
                n_files=nfiles, flags=flags)
    return head, files


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    if argv[1] not in ('--gc', '--cvm'):
        buf = open(argv[1], 'rb').read()
        head, files = parse(buf)
        if head is None:
            raise SystemExit('not an MSCF file')
        for k in ('version', 'cab_size', 'first_file', 'n_files', 'flags',
                  'folders'):
            print('%-14s %s' % (k, head[k]))
        print('%-14s %d bytes on disc' % ('actual', len(buf)))
        print()
        for name, size, stamp, at, fi, coff, doff in files:
            print('%-20s %10d  %s  attr 0x%04X  payload at 0x%X'
                  % (name, size, stamp, at, doff))
        return

    paths = [a for a in argv[2:] if not a.startswith('--')]
    rows = []
    for p in paths:
        if argv[1] == '--gc':
            d = gcm.Disc(p)
            items = [(q, o, l) for q, o, l, i in d.files()]
        else:
            d = cvm.CVM(p)
            items = d.files()
        for q, off, length in items:
            if not q.lower().endswith('.cab'):
                continue
            d.f.seek(off)
            buf = d.f.read(min(length, 4096))
            head, files = parse(buf)
            if head is None:
                continue
            for name, size, stamp, at, fi, coff, doff in files:
                rows.append((stamp, q, os.path.basename(p), name, size,
                             length, length - doff))
    if '--sorted' in argv:
        rows.sort()
    print('%-19s  %-26s %-14s %10s %10s %6s' %
          ('STAMP', 'CAB', 'MEMBER', 'DECLARED', 'STORED', 'RATIO'))
    for stamp, q, disc, name, size, length, payload in rows:
        print('%-19s  %-26s %-14s %10d %10d %5.2fx'
              % (stamp, q, name, size, payload,
                 size / float(payload) if payload else 0))
    print()
    print('%d archives' % len(rows))
    days = {}
    for stamp, q, disc, name, size, length, payload in rows:
        days[stamp[:10]] = days.get(stamp[:10], 0) + 1
    print()
    print('%-12s %s' % ('DAY', 'ARCHIVES'))
    for k in sorted(days):
        print('%-12s %d' % (k, days[k]))


if __name__ == '__main__':
    main(sys.argv)
