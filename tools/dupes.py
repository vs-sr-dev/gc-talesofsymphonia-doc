"""How much of each disc is the same bytes over again.

The question this repository exists to answer is what the two-disc split cost.
Both releases carry the same game in the same year; the GameCube one has to
put every asset a scene needs on the disc that scene plays from, and cannot
seek to the other spindle.  So the measurement is:

  * duplication *inside* one disc -- the ordinary kind, a shared asset copied
    next to each scene that wants it, which every title in this corpus has;
  * duplication *between* the two GameCube discs -- the part that exists only
    because there are two discs;
  * the same number on the single-disc PlayStation 2 release, which does not
    pay that cost and is the control.

Files are hashed whole, straight out of the file system, without extracting
anything.  Identical content under different names counts as duplication;
identical names with different content are reported separately, because on a
two-disc release that is how you tell a shared asset from a per-disc one.

    python tools/dupes.py --gc DISC1.gcm [DISC2.gcm]
    python tools/dupes.py --cvm FILE.CVM [FILE.CVM ...]
"""

import hashlib
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcm
import cvm


def digest(f, off, length):
    h = hashlib.sha1()
    f.seek(off)
    left = length
    while left:
        b = f.read(min(left, 1 << 20))
        if not b:
            break
        h.update(b)
        left -= len(b)
    return h.hexdigest()


def census(name, entries, f):
    """entries: [(path, offset, length)] -> (name, [(path,len,sha)])"""
    out = []
    for path, off, length in entries:
        out.append((path, length, digest(f, off, length)))
    return name, out


def report_one(name, rows):
    by = defaultdict(list)
    for path, length, sha in rows:
        by[sha].append((path, length))
    total = sum(r[1] for r in rows)
    distinct = sum(v[0][1] for v in by.values())
    dup = total - distinct
    print('%s' % name)
    print('  files                %d' % len(rows))
    print('  distinct by content  %d' % len(by))
    print('  bytes                %d' % total)
    print('  distinct bytes       %d' % distinct)
    print('  bytes that are a copy %d (%.1f%%)' %
          (dup, 100.0 * dup / total if total else 0))
    top = sorted(((len(v) - 1) * v[0][1], len(v), v[0][1], v[0][0])
                 for v in by.values() if len(v) > 1)
    top.reverse()
    if top:
        print()
        print('  %10s %7s %12s  %s' % ('WASTED', 'COPIES', 'EACH', 'FIRST'))
        for wasted, n, each, path in top[:20]:
            print('  %10d %7d %12d  %s' % (wasted, n, each, path))
    print()
    return by


def report_pair(n1, rows1, by1, n2, rows2, by2):
    shared = set(by1) & set(by2)
    shared_bytes = sum(by1[s][0][1] for s in shared)
    t1 = sum(r[1] for r in rows1)
    t2 = sum(r[1] for r in rows2)
    print('between %s and %s' % (n1, n2))
    print('  distinct contents on both   %d' % len(shared))
    print('  bytes of them (one copy)    %d' % shared_bytes)
    print('  as a share of %-14s %.1f%%' % (n1, 100.0 * shared_bytes / t1))
    print('  as a share of %-14s %.1f%%' % (n2, 100.0 * shared_bytes / t2))
    # instances, not distinct contents: what the second disc actually spends
    inst2 = sum(l for p, l, s in rows2 if s in shared)
    inst1 = sum(l for p, l, s in rows1 if s in shared)
    print('  bytes on %-19s %d (%.1f%%) are also on the other'
          % (n1, inst1, 100.0 * inst1 / t1))
    print('  bytes on %-19s %d (%.1f%%) are also on the other'
          % (n2, inst2, 100.0 * inst2 / t2))
    print()
    p1 = {p: (l, s) for p, l, s in rows1}
    p2 = {p: (l, s) for p, l, s in rows2}
    both = set(p1) & set(p2)
    same = [p for p in both if p1[p][1] == p2[p][1]]
    diff = sorted(p for p in both if p1[p][1] != p2[p][1])
    print('  same path on both discs     %d' % len(both))
    print('    identical content         %d (%d bytes)'
          % (len(same), sum(p1[p][0] for p in same)))
    print('    different content         %d' % len(diff))
    only1 = sorted(set(p1) - set(p2))
    only2 = sorted(set(p2) - set(p1))
    print('  only on %-19s %d files, %d bytes'
          % (n1, len(only1), sum(p1[p][0] for p in only1)))
    print('  only on %-19s %d files, %d bytes'
          % (n2, len(only2), sum(p2[p][0] for p in only2)))
    if diff:
        print()
        print('  same name, different bytes:')
        for p in diff[:40]:
            print('    %-40s %10d  %10d' % (p, p1[p][0], p2[p][0]))
        if len(diff) > 40:
            print('    ... and %d more' % (len(diff) - 40))
    if only1:
        print()
        print('  only on %s:' % n1)
        for p in only1[:40]:
            print('    %-40s %10d' % (p, p1[p][0]))
        if len(only1) > 40:
            print('    ... and %d more' % (len(only1) - 40))
    if only2:
        print()
        print('  only on %s:' % n2)
        for p in only2[:40]:
            print('    %-40s %10d' % (p, p2[p][0]))
        if len(only2) > 40:
            print('    ... and %d more' % (len(only2) - 40))
    print()


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    mode = argv[1]
    paths = [a for a in argv[2:] if not a.startswith('--')]
    sets = []
    for p in paths:
        if mode == '--gc':
            d = gcm.Disc(p)
            entries = [(q, o, l) for q, o, l, i in d.files()]
            sets.append(census(os.path.basename(p), entries, d.f))
        else:
            c = cvm.CVM(p)
            entries = [(q, o, l) for q, o, l in c.files()]
            sets.append(census(os.path.basename(p), entries, c.f))

    tables = []
    for name, rows in sets:
        tables.append((name, rows, report_one(name, rows)))

    if len(tables) > 1:
        for i in range(len(tables)):
            for j in range(i + 1, len(tables)):
                report_pair(tables[i][0], tables[i][1], tables[i][2],
                            tables[j][0], tables[j][1], tables[j][2])
        allrows = [r for _, rows, _ in tables for r in rows]
        report_one('all of them together', allrows)


if __name__ == '__main__':
    main(sys.argv)
