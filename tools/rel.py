"""List the GameCube relocatable modules and say which ones can be loaded.

`.rel` is Nintendo's relocatable-module format, this game's overlays.  Eight
ship on each disc and the executable names two.  This walks the header of each
one, hashes it, counts the strings that only a debug build carries, and
cross-references the names against the ones `main.dol` actually spells --
which is the whole test, because the loader takes a literal path and there is
no format string anywhere that could construct the others.

    python tools/rel.py DISC.gcm [--dol main.dol] [--strings]
"""

import hashlib
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcm

DEBUGGY = re.compile(r'Failed assertion|assert|\.c$|Warning:|Debug|debug')


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    d = gcm.Disc(argv[1])
    dol = d.dol()
    named = set(m.group()[:-1].decode().lower()
                for m in re.finditer(rb'[A-Za-z0-9_/]+\.rel\x00', dol))
    fmt = re.findall(rb'%[sd][A-Za-z0-9_.]*\.rel', dol)

    rows = []
    for p, off, length, i in d.files():
        if not p.lower().endswith('.rel'):
            continue
        d.f.seek(off)
        b = d.f.read(length)
        mid, nxt, prv, nsec, soff, noff, nsz, ver = struct.unpack_from(
            '>8I', b, 0)
        strs = [m.group().decode() for m in re.finditer(rb'[ -~]{6,}', b)]
        dbg = [s for s in strs if DEBUGGY.search(s)]
        rows.append((p, length, hashlib.sha1(b).hexdigest(), mid, nsec, ver,
                     len(strs), dbg))

    print('%-22s %10s %5s %5s %4s %8s %5s  %s' %
          ('FILE', 'BYTES', 'ID', 'SECS', 'VER', 'STRINGS', 'DEBUG', 'LOADED'))
    loadable = unreachable = 0
    for p, length, sha, mid, nsec, ver, ns, dbg in rows:
        hit = any(n.lstrip('/') == p.lstrip('/').lower() for n in named)
        print('%-22s %10d %5d %5d %4d %8d %5d  %s' %
              (p, length, mid, nsec, ver, ns, len(dbg),
               'yes' if hit else 'NO'))
        if hit:
            loadable += length
        else:
            unreachable += length
    print()
    print('names spelled in main.dol : %s' % ', '.join(sorted(named)))
    print('format strings that build a .rel name : %s' %
          (fmt if fmt else 'none'))
    print('distinct contents : %d of %d' %
          (len(set(r[2] for r in rows)), len(rows)))
    print('loadable    %10d bytes' % loadable)
    print('unreachable %10d bytes on this disc' % unreachable)
    print()
    for p, length, sha, mid, nsec, ver, ns, dbg in rows:
        if not dbg:
            continue
        print('%s' % p)
        for s in dbg[:12]:
            print('    %s' % s[:100])
        if len(dbg) > 12:
            print('    ... and %d more' % (len(dbg) - 12))
        print()


if __name__ == '__main__':
    main(sys.argv)
