"""Where every byte of a GameCube disc goes, and what is left over.

The image is 1,459,978,240 bytes whatever the game does, so the interesting
number is how much of it the game actually uses.  This walks the fixed
structures at the front, then the file system, then reports every gap between
one file and the next -- the space the mastering tool left behind, which on a
GameCube disc is padding rather than nothing and is where the disc's seek plan
shows up.

    python tools/layout.py DISC.gcm [--gaps N] [--order]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcm

SECTOR = 2048


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    d = gcm.Disc(argv[1])
    show = int(argv[argv.index('--gaps') + 1]) if '--gaps' in argv else 20

    spans = [('disc header', 0, 0x440),
             ('disc info (bi2)', 0x440, 0x2000),
             ('apploader', 0x2440, 0x20 + d.apploader_size +
              d.apploader_trailer),
             ('main.dol', d.dol_off, len(d.dol())),
             ('FST', d.fst_off, d.fst_size)]
    files = sorted(d.files(), key=lambda r: r[1])
    for p, o, l, i in files:
        spans.append((p, o, l))
    spans.sort(key=lambda s: s[1])

    print('%-34s %12s %12s %12s' % ('WHAT', 'START', 'END', 'BYTES'))
    for n, o, l in spans[:5]:
        print('%-34s %12d %12d %12d' % (n, o, o + l, l))
    print('%-34s %12d %12d %12d' %
          ('%d files' % len(files), files[0][1],
           max(o + l for p, o, l, i in files),
           sum(l for p, o, l, i in files)))
    print()

    gaps = []
    end = 0
    for n, o, l in spans:
        if o > end:
            gaps.append((end, o - end, n))
        end = max(end, o + l)
    tail = d.size - end
    used = sum(l for n, o, l in spans)
    total_gap = sum(g[1] for g in gaps)

    print('%-34s %12d' % ('image size', d.size))
    print('%-34s %12d (%.2f%%)' % ('claimed by a structure or file', used,
                                   100.0 * used / d.size))
    print('%-34s %12d (%.2f%%) in %d gaps' %
          ('between them', total_gap, 100.0 * total_gap / d.size, len(gaps)))
    print('%-34s %12d (%.2f%%)' % ('after the last file', tail,
                                   100.0 * tail / d.size))
    print('%-34s %12d (%.2f%%)' %
          ('unused in total', total_gap + tail,
           100.0 * (total_gap + tail) / d.size))
    print()
    gaps.sort(key=lambda g: -g[1])
    print('the %d largest gaps' % min(show, len(gaps)))
    print('  %-14s %12s %10s  %s' % ('AT', 'BYTES', 'SECTORS', 'BEFORE'))
    for o, n, what in gaps[:show]:
        print('  0x%012X %12d %10.1f  %s' % (o, n, n / float(SECTOR), what))
    print()
    small = sum(1 for o, n, w in gaps if n < SECTOR)
    print('%d of the %d gaps are under one sector: file-to-file alignment'
          % (small, len(gaps)))

    if '--order' in argv:
        print()
        print('files in disc order')
        print('  %-14s %12s  %s' % ('AT', 'BYTES', 'PATH'))
        for p, o, l, i in files:
            print('  0x%012X %12d  %s' % (o, l, p))


if __name__ == '__main__':
    main(sys.argv)
