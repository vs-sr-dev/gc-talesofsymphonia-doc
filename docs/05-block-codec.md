# The block codec on a big-endian machine

The format is specified once, in
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc).
This document records only what the two 2003–2004 builds add to it.

Section 8 of that specification had archived the Game Boy Advance result — the
2003 rebuild of *Phantasia* dropped the format and used the BIOS
`LZ77UnComp` — under the reading that a platform which supplies its own
decompression gets used. The GameCube supplies one, and it has ARAM and a DVD
drive and a file system with its own ideas about loading. It was the strongest
remaining test of that reading.

**The format survived it.**

---

## Finding it: the shortcut works on PowerPC

Section 7's shortcut is to scan for the immediates `4078` and `4079` — `RING −
18` and `RING − 17` — on the grounds that they belong to the packer, not to the
programmer, and nothing else loads 4,078. The encoding changes on PowerPC; the
constant does not. `tools/ring_sites.py` does both instruction sets.

```
main.dol, text1: 380912 words scanned, 12 sites

ADDRESS      WORD       FORM        IMM  ROUTINE
0x8005D0CC   0x20090FEF subfic     4079  0x8005D088 (+17 words)
0x8005D0DC   0x2C090FEF cmpwi      4079  0x8005D088 (+21 words)
0x8005D3E8   0x39400FEF addi       4079  0x8005D088 (+216 words)
0x8005D71C   0x20090FEE subfic     4078  0x8005D6D8 (+17 words)
0x8005D72C   0x2C090FEE cmpwi      4078  0x8005D6D8 (+21 words)
0x8005DA38   0x39400FEE addi       4078  0x8005D6D8 (+216 words)
0x800D635C   ...        (the same three, again)  0x800D6318
0x800D69AC   ...        (the same three, again)  0x800D6968
```

Twelve sites, four routines, and the offsets inside each routine are the same
three: `+17`, `+21`, `+216`. Two methods, linked twice.

**The two copies are byte-identical.** `0x8005D088` against `0x800D6318` is 404
words — 1,616 bytes — the same; `0x8005D6D8` against `0x800D6968` is 333 words,
1,332 bytes, the same. The linker pulled the same object in twice.

The same scan over the PlayStation 2 build finds five sites and four routines,
and there the two copies are **not** the same code at all — see
[06](06-decoder-lineage.md).

---

## Reading it: everything the source chose is still there

```
0x8005DA38  li       r10, 4078            ; the ring cursor
0x8005DA44  srwi     r0, r0, 1            ; shift the control register
0x8005DA48  rlwinm   r7, r0, 0, 23, 23    ; test bit 8
0x8005DA4C  bne      0x8005DA5C
0x8005DA50  lbz      r0, 0(r4)
0x8005DA58  ori      r0, r0, 0xFF00       ; flags = byte | 0xFF00
0x8005DA5C  rlwinm   r7, r0, 0, 31, 31    ; test bit 0
0x8005DA60  beq      0x8005DA84
0x8005DA64  lbz      r7, 0(r4)            ; literal
0x8005DA6C  stbx     r7, r6, r10          ; into the ring
0x8005DA74  rlwinm   r10, r10, 0, 20, 31  ; cursor &= 0x0FFF
...
0x8005DA84  lbz      r9, 1(r4)            ; the two-byte token
0x8005DA8C  lbz      r11, 0(r4)
0x8005DA94  rlwinm   r8, r9, 0, 28, 31    ; length  = b1 & 0x0F
0x8005DA98  rlwinm   r9, r9, 4, 20, 23    ; ref hi  = b1 >> 4
0x8005DA9C  addi     r8, r8, 2
0x8005DAA4  rlwimi   r9, r11, 0, 24, 31   ; ref lo  = b0
...
0x8005DAC0  srwi     r11, r11, 3          ; the copy loop, unrolled by 8
```

Every constant the specification says belongs to the format is present and
unchanged:

| Trait | Specification | GameCube 2003 |
|---|---|---|
| Control register refill | `flags = byte \| 0xFF00` | `ori r0, r0, 0xFF00` |
| Control bits | LSB first, `1` = literal | `rlwinm 0,31,31`, `beq` to the token path |
| Ring | 4,096 bytes | cursor masked `rlwinm 0,20,31` = `& 0x0FFF` |
| Cursor start | `RING − 18` / `RING − 17` | `li r10, 4078` / `li r10, 4079` |
| Nibble order | **PlayStation dialect**: length `b1 & 0x0F`, reference top `b1 >> 4` | identical |
| Match length | code + 3, so 3–18 | `addi r8, r8, 2` plus the loop's own byte |
| Preload | synthetic `(i, 0x00)` and `(i, 0xFF)` pairs below the cursor | present — the loop alternates a running counter with `0` and with `li r11, 255` at `0x8005D204` |
| Copy loop unroll | eight | `srwi r11, r11, 3` |

**There is no third dialect.** The split is still 1995/1997, now across five
titles, four consoles, eight years and both byte orders.

---

## The nine-byte header stayed little-endian

This was the field most likely to produce a third dialect, and it did not.

```
Kratos.bin @0x1EA00   header  01 1e 21 00 00 e4 3c 00 00
   little-endian: method 1, packed 8478, unpacked 15588   <- decodes
   big-endian:    method 1, packed 505479168, unpacked 3829137408
```

The container around it *is* big-endian — the archive that holds these blocks
counts its members with a big-endian `u32` — so the two byte orders sit next to
each other in the same file, four bytes apart.

The reason is in section 1 of the specification, written before anyone looked
at a GameCube: *the PlayStation decoder assembles all four bytes, one `lbu` at
a time, because a container can place a block at any alignment.* Code that
reads a `u32` a byte at a time and shifts them together has no endianness; it
has whatever endianness its constants say. Port it to a big-endian machine and
it keeps reading little-endian sizes, and nothing anywhere reports an error.

The packer never had to be told about the GameCube, and was not.

---

## The census

`tools/census.py` scans every file in the file system for the header shape and
keeps only the offsets whose decoded length matches the length the header
declares. The decoder is `tales_block.py`, copied from the corpus with **no
edits and no GameCube branch**.

```
=== tos-gc-d1.gcm                === tos-gc-d2.gcm
  files with blocks   22 of 1602     files with blocks   22 of 1598
  blocks              487            blocks              487
  methods             1: 185         methods             1: 185
                      3: 302                             3: 302
  packed bytes        79,744,495     packed bytes        79,744,495
  unpacked bytes     143,368,204     unpacked bytes     143,368,204
  ratio               1.80x          ratio               1.80x

  validation on /Kratos.bin: 6 blocks at step 1, 6 at step 32, 0 missed
```

**487 of 487 blocks decode to the length their headers declare, on both discs,
under the unmodified reference decoder.** The two discs' figures are identical
to the byte, because all twenty-two files that contain blocks are among the
1,588 duplicated on both discs — which is [07](07-duplication.md)'s subject.

Where the blocks are:

| File | Size | Blocks | Packed | Unpacked |
|---|---:|---:|---:|---:|
| `/BTL/BTLenemy.dat` | 77,952,000 | 251 | 77,945,676 | 139,790,048 |
| `/npc_all.bin` | 87,184,096 | 101 | 651,197 | 1,368,668 |
| `/BTL/BTLusual.dat` | 935,680 | 1 | 130,512 | 265,376 |
| nineteen character `.bin` files | | 134 | 1,017,110 | 1,944,112 |

Two things about that table matter.

**The codec is no longer the disc's format; it is one of the disc's formats.**
Twenty-two files out of 1,602. On the 2002 PlayStation 2 disc the codec's
output was 329 MB of a 3.2 GB disc and reached almost every asset; here it is
79.7 MB of 1.38 GB and reaches battle enemy data and character models. The
forty-five `.cab` archives described in [04](04-executables-and-tools.md) are
compressed with something else entirely, and they hold most of the character
art.

**The packer's block size grew by a factor of thirty.** The largest genuine
block here is **1,007,213 packed bytes**, inside `/BTL/BTLenemy.dat`. Across
the four earlier titles the largest was around thirty kilobytes. Something in
the packer's driver changed; the format did not.

[`reports/gc-codec-census.txt`](../reports/gc-codec-census.txt),
[`reports/gc-codec-census-d2.txt`](../reports/gc-codec-census-d2.txt),
[`reports/ps2-codec-census.txt`](../reports/ps2-codec-census.txt).
