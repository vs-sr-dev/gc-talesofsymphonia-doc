"""Read a GameCube disc image: header, apploader, DOL and the FST.

A GameCube disc is not ISO 9660.  The first 0x440 bytes are a Nintendo disc
header, the next 0x2000 are the disc-info block the apploader reads, then the
apploader itself, and the file system is a flat array of twelve-byte records
followed by a string table -- the FST.  Everything is big-endian, which is the
first thing that matters for a series that had only ever shipped on
little-endian consoles.

    python tools/gcm.py DISC.gcm --header
    python tools/gcm.py DISC.gcm --list
    python tools/gcm.py DISC.gcm --extract OUTDIR/
    python tools/gcm.py DISC.gcm --dol-sections
"""

import os
import struct
import sys

SECTOR = 2048


def u32(b, o):
    return struct.unpack_from('>I', b, o)[0]


class Disc(object):

    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        self.size = os.path.getsize(path)
        h = self.read(0, 0x2440)
        self.head = h
        self.game_code = h[0:4]
        self.maker_code = h[4:6]
        self.disc_id = h[6]
        self.version = h[7]
        self.audio_streaming = h[8]
        self.stream_buf_size = h[9]
        self.magic = u32(h, 0x1C)
        self.title = h[0x20:0x400].split(b'\0')[0]
        self.debug_off = u32(h, 0x400)
        self.debug_addr = u32(h, 0x404)
        self.dol_off = u32(h, 0x420)
        self.fst_off = u32(h, 0x424)
        self.fst_size = u32(h, 0x428)
        self.fst_max = u32(h, 0x42C)
        self.user_pos = u32(h, 0x430)
        self.user_len = u32(h, 0x434)
        self.bi2 = h[0x440:0x2440]
        self.apploader_date = self.read(0x2440, 16).split(b'\0')[0]
        al = self.read(0x2450, 16)
        self.apploader_entry = u32(al, 0)
        self.apploader_size = u32(al, 4)
        self.apploader_trailer = u32(al, 8)
        self._fst = None

    def read(self, off, n):
        self.f.seek(off)
        return self.f.read(n)

    # -- file system ------------------------------------------------------

    def fst(self):
        """[(path, offset, length, is_dir, index)] in FST order, files only
        unless is_dir is asked for."""
        if self._fst is not None:
            return self._fst
        raw = self.read(self.fst_off, self.fst_size)
        n = u32(raw, 8)
        strings = raw[n * 12:]
        out = []
        stack = [(n, '')]
        i = 1
        while i < n:
            flags = raw[i * 12]
            noff = u32(raw, i * 12) & 0xFFFFFF
            a = u32(raw, i * 12 + 4)
            b = u32(raw, i * 12 + 8)
            end = strings.find(b'\0', noff)
            name = strings[noff:end].decode('shift_jis', 'replace')
            while len(stack) > 1 and i >= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            path = parent + '/' + name if parent else '/' + name
            if flags:
                out.append((path, a, b, True, i))
                stack.append((b, path))
            else:
                out.append((path, a, b, False, i))
            i += 1
        self._fst = out
        return out

    def files(self):
        return [(p, o, l, i) for p, o, l, d, i in self.fst() if not d]

    # -- executable -------------------------------------------------------

    def dol(self):
        """The main DOL as raw bytes.  Its length is the end of its last
        section, which is the only place the size is written down."""
        h = self.read(self.dol_off, 0x100)
        end = 0x100
        for i in range(18):
            off = u32(h, i * 4)
            size = u32(h, 0x90 + i * 4)
            if off and size:
                end = max(end, off + size)
        return self.read(self.dol_off, end)

    def dol_sections(self):
        h = self.read(self.dol_off, 0x100)
        secs = []
        for i in range(18):
            off = u32(h, i * 4)
            addr = u32(h, 0x48 + i * 4)
            size = u32(h, 0x90 + i * 4)
            if size:
                secs.append(('text%d' % i if i < 7 else 'data%d' % (i - 7),
                             off, addr, size))
        secs.append(('bss', 0, u32(h, 0xD8), u32(h, 0xDC)))
        return secs, u32(h, 0xE0)


def header(d):
    print('%-22s %s' % ('image', os.path.basename(d.path)))
    print('%-22s %d bytes' % ('image size', d.size))
    print('%-22s %s' % ('game code',
                        d.game_code.decode('ascii', 'replace')))
    print('%-22s %s' % ('maker code',
                        d.maker_code.decode('ascii', 'replace')))
    print('%-22s %d' % ('disc number', d.disc_id))
    print('%-22s %d' % ('version', d.version))
    print('%-22s %d' % ('audio streaming', d.audio_streaming))
    print('%-22s %d' % ('stream buffer size', d.stream_buf_size))
    print('%-22s 0x%08X %s' % ('magic', d.magic,
                               'ok' if d.magic == 0xC2339F3D else 'BAD'))
    print('%-22s %s' % ('title',
                        d.title.decode('shift_jis', 'replace')))
    print('%-22s 0x%08X' % ('debug monitor at', d.debug_off))
    print('%-22s 0x%08X' % ('debug monitor load', d.debug_addr))
    print('%-22s %s' % ('apploader date',
                        d.apploader_date.decode('ascii', 'replace')))
    print('%-22s %d bytes, entry 0x%08X, trailer %d' %
          ('apploader', d.apploader_size, d.apploader_entry,
           d.apploader_trailer))
    print('%-22s 0x%08X' % ('DOL at', d.dol_off))
    print('%-22s 0x%08X, %d bytes (max %d)' %
          ('FST at', d.fst_off, d.fst_size, d.fst_max))
    print('%-22s 0x%08X, %d bytes' % ('user area', d.user_pos, d.user_len))
    fs = d.fst()
    files = [x for x in fs if not x[3]]
    dirs = [x for x in fs if x[3]]
    total = sum(x[2] for x in files)
    print('%-22s %d files, %d directories, %d bytes' %
          ('file system', len(files), len(dirs), total))


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    d = Disc(argv[1])
    if '--header' in argv:
        header(d)
    elif '--list' in argv:
        print('%-12s %-12s %10s  %s' % ('OFFSET', 'END', 'BYTES', 'PATH'))
        for p, o, l, is_dir, i in d.fst():
            if is_dir:
                print('%-12s %-12s %10s  %s/' % ('', '', '', p))
            else:
                print('0x%08X   0x%08X   %10d  %s' % (o, o + l, l, p))
        f = d.files()
        print()
        print('%d files, %d bytes' % (len(f), sum(x[2] for x in f)))
    elif '--dol-sections' in argv:
        secs, entry = d.dol_sections()
        print('%-8s %-12s %-12s %10s' % ('NAME', 'FILE', 'ADDR', 'SIZE'))
        for n, off, addr, size in secs:
            print('%-8s 0x%08X   0x%08X   %10d' % (n, off, addr, size))
        print('entry 0x%08X' % entry)
    elif '--extract' in argv:
        out = argv[argv.index('--extract') + 1]
        for p, o, l, i in d.files():
            dst = os.path.join(out, p.lstrip('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as g:
                d.f.seek(o)
                left = l
                while left:
                    chunk = d.f.read(min(left, 1 << 20))
                    g.write(chunk)
                    left -= len(chunk)
        # the pieces that are not in the file system
        for name, off, size in (('boot.bin', 0, 0x440),
                                ('bi2.bin', 0x440, 0x2000),
                                ('apploader.img', 0x2440,
                                 0x20 + d.apploader_size +
                                 d.apploader_trailer),
                                ('fst.bin', d.fst_off, d.fst_size)):
            with open(os.path.join(out, name), 'wb') as g:
                g.write(d.read(off, size))
        with open(os.path.join(out, 'main.dol'), 'wb') as g:
            g.write(d.dol())
        print('extracted %d files to %s' % (len(d.files()), out))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv)
