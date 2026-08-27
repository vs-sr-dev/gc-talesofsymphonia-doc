"""Read an RVZ container and write the GameCube disc image inside it.

The two GameCube discs arrive as RVZ, Dolphin's compressed disc format, and
nothing in this repository can read that.  This file is the smallest reader
that gets the bytes back: it parses the two headers, decompresses the group
table and the raw-data table, and walks the groups in order.

Three things make RVZ more than a zip of the image, and all three matter to
the documentation rather than merely to the extraction:

  * groups are compressed independently, so the compressed size of a group is
    a cheap proxy for how compressible that stretch of the disc is;
  * a group may be *packed*, meaning it is a sequence of runs that are either
    literal bytes or a note saying "the next N bytes are Nintendo padding,
    generated from this seed" -- so the container tells us directly which
    sectors of the disc are padding and which are content, without us having
    to guess from the file system;
  * the padding generator is the lagged Fibonacci one Nintendo's mastering
    tool used, reimplemented here.

    python tools/rvz.py IN.rvz --info
    python tools/rvz.py IN.rvz --junk-map
    python tools/rvz.py IN.rvz -o OUT.gcm
"""

import hashlib
import struct
import sys

try:
    import zstandard
except ImportError:
    zstandard = None
import bz2
import lzma

NONE, PURGE, BZIP2, LZMA, LZMA2, ZSTD = range(6)
CNAME = {NONE: 'none', PURGE: 'purge', BZIP2: 'bzip2',
         LZMA: 'lzma', LZMA2: 'lzma2', ZSTD: 'zstd'}


class LFG(object):
    """The lagged Fibonacci generator that fills the unused parts of the disc.

    A GameCube disc is not zero padded.  Everything not covered by a file is
    filled with the output of this generator, which is why a disc image does
    not compress to nothing and why RVZ bothers to special-case it at all.

    RVZ stores the generator state verbatim -- seventeen big-endian words,
    sixty-eight bytes, per padding run -- so nothing about the seed has to be
    guessed here.  The recurrence extends those seventeen words to five
    hundred and twenty-one, steps the whole array four times, and then hands
    out the words in order.
    """

    K = 521
    J = 32
    SEED_WORDS = 17

    def __init__(self, seed_words):
        b = list(seed_words) + [0] * (self.K - self.SEED_WORDS)
        for i in range(self.SEED_WORDS, self.K):
            b[i] = ((b[i - 17] << 23) ^ (b[i - 16] >> 9) ^ b[i - 1]) & 0xFFFFFFFF
        self.buf = b
        for _ in range(4):
            self._advance()
        self.pos = 0

    def _advance(self):
        b = self.buf
        for i in range(self.J):
            b[i] ^= b[i + self.K - self.J]
        for i in range(self.J, self.K):
            b[i] ^= b[i - self.J]
        self.pos = 0

    def bytes(self, n):
        out = bytearray()
        while len(out) < n:
            if self.pos >= self.K:
                self._advance()
            take = min((n - len(out) + 3) // 4, self.K - self.pos)
            out += struct.pack('>%dI' % take,
                               *self.buf[self.pos:self.pos + take])
            self.pos += take
        return bytes(out[:n])


SEED_BYTES = LFG.SEED_WORDS * 4


def _decompress(kind, data, out_size, cdata):
    if kind == NONE:
        return data
    if kind == ZSTD:
        if zstandard is None:
            raise SystemExit('this file needs the zstandard module')
        return zstandard.ZstdDecompressor().decompress(
            data, max_output_size=out_size)
    if kind == BZIP2:
        return bz2.decompress(data)
    if kind == LZMA:
        return lzma.LZMADecompressor(lzma.FORMAT_ALONE).decompress(
            cdata + b'\xff' * 8 + data)
    if kind == LZMA2:
        return lzma.LZMADecompressor(
            lzma.FORMAT_RAW,
            filters=[{'id': lzma.FILTER_LZMA2,
                      'dict_size': 1 << 23}]).decompress(data)
    raise SystemExit('unsupported compression %d' % kind)


class RVZ(object):

    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        h1 = self.f.read(0x48)
        if h1[:4] not in (b'RVZ\x01', b'WIA\x01'):
            raise SystemExit('%s: not RVZ or WIA' % path)
        self.magic = h1[:4]
        self.version, self.version_compatible, h2_size = struct.unpack_from(
            '>3I', h1, 4)
        self.iso_size, self.wia_size = struct.unpack_from('>2Q', h1, 0x24)

        h2 = self.f.read(h2_size)
        (self.disc_type, self.compression, self.level,
         self.chunk_size) = struct.unpack_from('>4i', h2, 0)
        self.disc_header = h2[0x10:0x90]
        (self.n_part, self.part_entry_size,
         self.part_off) = struct.unpack_from('>IIQ', h2, 0x90)
        (self.n_raw, self.raw_off,
         self.raw_size) = struct.unpack_from('>IQI', h2, 0xB4)
        (self.n_group, self.group_off,
         self.group_size) = struct.unpack_from('>IQI', h2, 0xC4)
        cd_size = h2[0xD4]
        self.cdata = h2[0xD5:0xD5 + cd_size]

        self.group_stride = 12 if self.magic == b'RVZ\x01' else 8
        self.raw = self._table(self.raw_off, self.raw_size, self.n_raw * 24)
        self.groups = self._table(self.group_off, self.group_size,
                                  self.n_group * self.group_stride)

    def _table(self, off, packed, unpacked):
        self.f.seek(off)
        return _decompress(self.compression, self.f.read(packed),
                           unpacked, self.cdata)

    def raw_entries(self):
        for i in range(self.n_raw):
            yield struct.unpack_from('>QQII', self.raw, i * 24)

    def group(self, idx):
        """(file offset, packed size, is_compressed, rvz_packed_size)"""
        o = idx * self.group_stride
        off, size = struct.unpack_from('>II', self.groups, o)
        packed = 0
        if self.group_stride == 12:
            packed = struct.unpack_from('>I', self.groups, o + 8)[0]
        return off << 2, size & 0x7FFFFFFF, bool(size & 0x80000000), packed

    def group_data(self, idx, exp, generate=True):
        off, size, comp, packed = self.group(idx)
        if size == 0:
            return b'\0' * exp, 0, 0, 0
        self.f.seek(off)
        raw = self.f.read(size)
        stored = size
        if comp:
            raw = _decompress(self.compression, raw,
                              packed if packed else exp, self.cdata)
        if packed:
            data, lit, junk, seeds = _unpack(raw, exp, generate)
            return data, lit, junk, stored, seeds
        return raw, len(raw), 0, stored, []


def _unpack(buf, exp, generate=True):
    """Expand an RVZ-packed group.  Returns (data, literal bytes, junk bytes).

    With generate=False the padding runs are left as zeroes.  Reconstructing
    them costs real time and nothing in this repository reads them; the map of
    where they are is the part that carries information.
    """
    out = bytearray()
    i = 0
    lit = junk = 0
    seeds = []
    n = len(buf)
    while i + 4 <= n and len(out) < exp:
        size = struct.unpack_from('>I', buf, i)[0]
        i += 4
        is_junk = bool(size & 0x80000000)
        size &= 0x7FFFFFFF
        if is_junk:
            seed = struct.unpack_from('>17I', buf, i)
            i += SEED_BYTES
            if not generate or not any(seed):
                # An all-zero state generates all-zero output.  Both GameCube
                # discs here use only that state, so the expensive path below
                # never runs on them -- see docs/02-the-two-discs.md.
                out += bytes(size)
            else:
                out += LFG(seed).bytes(size)
            junk += size
            seeds.append((size, seed))
        else:
            out += buf[i:i + size]
            i += size
            lit += size
    if len(out) < exp:
        out += b'\0' * (exp - len(out))
    return bytes(out[:exp]), lit, junk, seeds


def info(r):
    print('%-24s %s' % ('container', r.magic[:3].decode()))
    print('%-24s %d.%d.%d' % ('version', (r.version >> 24) & 0xFF,
                              (r.version >> 16) & 0xFF,
                              (r.version >> 8) & 0xFF))
    print('%-24s %s, level %d, chunk %d' %
          ('compression', CNAME.get(r.compression, '?'), r.level,
           r.chunk_size))
    print('%-24s %d (%s)' % ('disc type', r.disc_type,
                             {1: 'GameCube', 2: 'Wii'}.get(r.disc_type, '?')))
    print('%-24s %d bytes' % ('image size', r.iso_size))
    print('%-24s %d bytes (%.1f%% of image)' %
          ('container size', r.wia_size, 100.0 * r.wia_size / r.iso_size))
    print('%-24s %s' % ('game id',
                        r.disc_header[:6].decode('ascii', 'replace')))
    print('%-24s %s' % ('title', r.disc_header[0x20:0x60].rstrip(b'\0')
                        .decode('ascii', 'replace')))
    print('%-24s %d' % ('raw data entries', r.n_raw))
    print('%-24s %d' % ('groups', r.n_group))
    print('%-24s %d' % ('partition entries', r.n_part))
    print()
    print('%-10s %14s %14s %8s %8s' %
          ('raw entry', 'offset', 'size', 'group', 'count'))
    for i, (off, size, gi, gn) in enumerate(r.raw_entries()):
        print('%-10d %14d %14d %8d %8d' % (i, off, size, gi, gn))


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    r = RVZ(argv[1])
    if '--info' in argv:
        info(r)
        return
    junkmap = '--junk-map' in argv
    out = None
    if '-o' in argv:
        out = open(argv[argv.index('-o') + 1], 'wb')
    if out:
        out.write(r.disc_header)
    h = hashlib.sha1()
    h.update(r.disc_header)
    tot_lit = tot_junk = tot_stored = 0
    nonzero_seeds = 0
    runs = []
    for off, size, gi, gn in r.raw_entries():
        # A raw data entry is stored aligned down to a whole chunk, so the
        # first group can begin before the offset the entry declares.  The
        # bytes in front of it are the disc header, which lives in the
        # container header as well.
        skew = off % r.chunk_size
        off -= skew
        size += skew
        pos = off
        for g in range(gn):
            exp = min(r.chunk_size, off + size - pos)
            data, lit, junk, stored, seeds = r.group_data(
                gi + g, exp, out is not None)
            for _sz, _sd in seeds:
                if any(_sd):
                    nonzero_seeds += 1
            tot_lit += lit
            tot_junk += junk
            tot_stored += stored
            if junkmap and junk:
                runs.append((pos, exp, lit, junk))
            if out:
                out.seek(pos)
                out.write(data)
            h.update(data)
            pos += exp
    if out:
        out.close()
    if junkmap:
        print('%-14s %10s %12s %12s' %
              ('offset', 'sector', 'literal', 'junk'))
        for pos, exp, lit, junk in runs:
            print('%-14d %10d %12d %12d' % (pos, pos // 2048, lit, junk))
        print()
    print('literal bytes %d, junk bytes %d, sum %d, image %d' %
          (tot_lit, tot_junk, tot_lit + tot_junk, r.iso_size))
    print('stored bytes  %d' % tot_stored)
    print('padding runs with a non-zero generator state: %d' % nonzero_seeds)
    print('sha1 %s' % h.hexdigest())


if __name__ == '__main__':
    main(sys.argv)
