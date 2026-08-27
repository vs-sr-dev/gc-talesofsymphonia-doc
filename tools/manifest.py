"""Compare the file names an executable knows about with the ones that shipped.

Both executables carry long runs of plain-text asset names -- the tables the
loader indexes into.  Cross-referencing them against the file system finds two
kinds of thing.  Names that are on the disc but not in the table are assets
some other index reaches.  Names that are in the table but *not* on the disc
are the interesting ones: something the build could still ask for and would
not get, which is usually a feature that was cut after the code that loads it
was written.

    python tools/manifest.py EXE --gc DISC.gcm [DISC2.gcm]
    python tools/manifest.py EXE --cvm A.CVM [B.CVM ...]
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcm
import cvm

NAME = re.compile(rb'[A-Za-z0-9_./\\-]{1,60}\.[A-Za-z0-9]{1,4}\x00')
# extensions that are source code or a host path, not a shipped asset
NOT_ASSETS = {'c', 'cpp', 'h', 's', 'obj', 'o', 'exe', 'dll'}


def referenced(path):
    data = open(path, 'rb').read()
    out = {}
    for m in NAME.finditer(data):
        s = m.group()[:-1].decode('ascii')
        ext = s.rsplit('.', 1)[1].lower()
        if ext in NOT_ASSETS:
            continue
        if s.startswith('..') or ':' in s:
            continue
        out.setdefault(s.replace('\\', '/').lstrip('/').upper(), m.start())
    return out


def shipped(mode, paths):
    out = {}
    for p in paths:
        if mode == '--gc':
            d = gcm.Disc(p)
            names = [(q, l) for q, o, l, i in d.files()]
        else:
            c = cvm.CVM(p)
            names = [(q, l) for q, o, l in c.files()]
        for q, l in names:
            key = q.lstrip('/').upper()
            out[key] = (os.path.basename(p), l)
            # the tables usually spell a name without its directory
            out.setdefault(os.path.basename(key), (os.path.basename(p), l))
    return out


def main(argv):
    if len(argv) < 4:
        raise SystemExit(__doc__)
    exe = argv[1]
    mode = argv[2]
    paths = [a for a in argv[3:] if not a.startswith('--')]
    ref = referenced(exe)
    have = shipped(mode, paths)

    missing = sorted(k for k in ref if k not in have)
    unref = sorted(k for k in have
                   if k not in ref and os.path.basename(k) not in ref)

    print('%-34s %s' % ('executable', os.path.basename(exe)))
    print('%-34s %s' % ('file systems',
                        ', '.join(os.path.basename(p) for p in paths)))
    print('%-34s %d' % ('names spelled in the executable', len(ref)))
    print('%-34s %d' % ('names present on disc', len(have)))
    print('%-34s %d' % ('named but not present', len(missing)))
    print('%-34s %d' % ('present but not named', len(unref)))
    print()
    if missing:
        print('named by the executable, absent from every file system:')
        for k in missing:
            print('  %-44s at 0x%06X' % (k, ref[k]))
        print()
    if unref:
        print('present but never named (first 60):')
        for k in unref[:60]:
            print('  %-44s %s %d' % (k, have[k][0], have[k][1]))
        if len(unref) > 60:
            print('  ... and %d more' % (len(unref) - 60))


if __name__ == '__main__':
    main(sys.argv)
