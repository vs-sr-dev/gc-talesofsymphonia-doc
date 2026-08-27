"""Find and check every block the codec produced, on either release.

The test is the one section 7 of the specification prescribes and the one the
2002 pipeline used: scan for the nine-byte header, decode with the shared
reference decoder, and keep only the offsets whose output length matches the
length the header itself declares.  Nothing here knows anything about the
GameCube; the decoder is `tales_block.py` copied from the corpus without a
single edit, and that is the point of the exercise.

Blocks on both these discs sit at 32-byte boundaries, so the scan steps by 32
by default.  That is a claim, not an assumption, and `--validate FILE` checks
it: it rescans one file at every byte offset and reports whether the coarse
step missed anything.

Two bounds are applied and both are reported rather than hidden.  A header is
only tried if it claims a packed size of at most `--max` bytes; the reference
decoder itself allows sixteen megabytes, which on a disc holding a gigabyte of
video means thousands of random sixteen-megabyte decodes that cannot succeed
and take a minute each.  The default is one megabyte, and the count of headers
skipped for exceeding it is printed so the bound can be audited.  On these
discs it is a real bound and not a comfortable one: the largest genuine block
found is 1,007,213 packed bytes, in `/BTL/BTLenemy.dat`, which is thirty times
larger than any block in the four earlier titles and only four percent under
the cap.  Re-running that one file with `--max 16777216` finds the same 251
blocks and skips nothing.

The second bound is a work budget.  A header that passes the shape test almost
always fails to decode, but finding that out costs a decode, and some files --
the PlayStation 2 field data especially -- produce enough false headers that a
quarter-megabyte file takes eight seconds to clear.  `--budget` caps the total
bytes of decoder output *attempted* per file; a file that exceeds it stops
being scanned and is named in the report, so no file is ever quietly
half-covered.  The GameCube discs never reach the default.

    python tools/census.py --gc DISC.gcm [--step N] [--max N] [--budget MB]
                                         [--validate NAME]
    python tools/census.py --cvm FILE.CVM [...]
"""

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tales_block
import gcm
import cvm

skipped_big = 0
BUDGET_HIT = 'budget'


def scan(buf, step, maxpacked, budget=None):
    """tales_block.scan, with the size bound above.  The decoding is the
    reference decoder's, untouched; only the choice of which headers to try
    is ours."""
    global skipped_big
    hits = []
    spent = 0
    n = len(buf) - 9
    for off in range(0, n, step):
        if not tales_block.plausible(buf, off, tales_block.PSX):
            continue
        _, packed, unpacked = tales_block.header(buf, off)
        if packed > maxpacked:
            skipped_big += 1
            continue
        if budget is not None:
            spent += packed
            if spent > budget:
                hits.append(BUDGET_HIT)
                return hits
        try:
            out = tales_block.unpack(buf, off, tales_block.PSX)
        except tales_block.BlockError:
            continue
        if len(out) == unpacked:
            hits.append((off, buf[off], packed, unpacked))
    return hits


def entries(mode, path):
    if mode == '--gc':
        d = gcm.Disc(path)
        return d.f, [(p, o, l) for p, o, l, i in d.files()]
    c = cvm.CVM(path)
    return c.f, c.files()


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    mode = argv[1]
    step = int(argv[argv.index('--step') + 1]) if '--step' in argv else 32
    maxpacked = (int(argv[argv.index('--max') + 1])
                 if '--max' in argv else 1 << 20)
    budget = (int(argv[argv.index('--budget') + 1]) << 20
              if '--budget' in argv else 64 << 20)
    validate = (argv[argv.index('--validate') + 1]
                if '--validate' in argv else None)
    paths = [a for a in argv[2:] if not a.startswith('--')
             and a != str(step) and a != validate]

    grand = Counter()
    gpacked = gunpacked = 0
    for path in paths:
        f, files = entries(mode, path)
        rows = []
        over = []
        methods = Counter()
        packed = unpacked = 0
        nblocks = 0
        for p, off, length in files:
            if length < 16:
                continue
            f.seek(off)
            buf = f.read(length)
            hits = scan(buf, step, maxpacked, budget)
            if hits and hits[-1] is BUDGET_HIT:
                hits.pop()
                over.append(p)
            if not hits:
                continue
            bp = sum(h[2] for h in hits)
            bu = sum(h[3] for h in hits)
            for h in hits:
                methods[h[1]] += 1
            rows.append((p, length, len(hits), bp, bu))
            nblocks += len(hits)
            packed += bp
            unpacked += bu
        print('=== %s' % os.path.basename(path))
        print('  files with blocks   %d of %d' % (len(rows), len(files)))
        print('  blocks              %d' % nblocks)
        print('  methods             %s' %
              ', '.join('%d: %d' % (k, v) for k, v in sorted(methods.items())))
        print('  packed bytes        %d' % packed)
        print('  unpacked bytes      %d' % unpacked)
        if packed:
            print('  ratio               %.2fx' % (unpacked / float(packed)))
        print('  headers skipped for claiming more than %d packed bytes  %d'
              % (maxpacked, skipped_big))
        print('  files abandoned on the %d MB decode budget  %d'
              % (budget >> 20, len(over)))
        for q in over:
            print('      %s' % q)
        print()
        print('  %-40s %12s %7s %12s %12s' %
              ('FILE', 'SIZE', 'BLOCKS', 'PACKED', 'UNPACKED'))
        for p, length, n, bp, bu in sorted(rows, key=lambda r: -r[3])[:40]:
            print('  %-40s %12d %7d %12d %12d' % (p, length, n, bp, bu))
        if len(rows) > 40:
            print('  ... and %d more files' % (len(rows) - 40))
        print()
        grand.update(methods)
        gpacked += packed
        gunpacked += unpacked

        if validate:
            for p, off, length in files:
                if os.path.basename(p) != validate:
                    continue
                f.seek(off)
                buf = f.read(length)
                fine = scan(buf, 1, maxpacked)
                coarse = scan(buf, step, maxpacked)
                missed = [h for h in fine if h not in coarse]
                print('  validation on %s: %d blocks at step 1, %d at step %d,'
                      ' %d missed' % (p, len(fine), len(coarse), step,
                                      len(missed)))
                for h in missed:
                    print('    missed 0x%X method %d' % (h[0], h[1]))
                print()

    if len(paths) > 1:
        print('=== all of them')
        print('  methods       %s' %
              ', '.join('%d: %d' % (k, v) for k, v in sorted(grand.items())))
        print('  blocks        %d' % sum(grand.values()))
        print('  packed bytes  %d' % gpacked)
        print('  unpacked      %d' % gunpacked)
        if gpacked:
            print('  ratio         %.2fx' % (gunpacked / float(gpacked)))


if __name__ == '__main__':
    main(sys.argv)
