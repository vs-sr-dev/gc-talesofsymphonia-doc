# Open questions

Everything here is either unmeasured, measured badly, or measured and
unexplained. Nothing in this file has been softened in the documents it came
from.

---

## Measured and unexplained

### Why 4,080?

The 2004 PlayStation 2 build clears the dictionary by calling a quadword
`bzero` with a length of **4,080** where every earlier build clears **4,078**.
4,080 divides by sixteen and 4,078 does not, so the round number is explained;
what is not explained is why the change was made at all. The clear is a
one-off cost at the start of a block and the loop it replaces is nine
instructions. It is a hand edit to a routine nobody had edited since 1997, for
a saving that cannot matter, and it is the only source-level change to the
decoder anywhere in the corpus. [06](06-decoder-lineage.md)

### Why two differently compiled copies on one PlayStation 2 disc?

`SLPS_254.00` carries the decoder pair twice: 1,104 + 768 bytes at
`0x001C93D0`, and 1,520 + 1,176 bytes at `0x00242C5C`, with 2 identical words
out of 276 between them. The second is far more heavily unrolled. On the
GameCube the two copies are byte-identical, which is what a linker pulling one
object in twice looks like. Two compilations with different settings would
explain the PlayStation 2 pair; so would two hand variants. Nothing on the
disc distinguishes them.

*Destiny 2* in 2002 had a version of this question — its two copies were on
two different processors and shared 24.3% of their opcode sequence — and it is
still open there too.

### Why did the packer's block size grow thirtyfold?

The largest block in the four titles up to 2002 is around 30 KB. The largest
here is **1,007,213 packed bytes**, in `/BTL/BTLenemy.dat`, and 251 blocks in
that one file average 310 KB. The format has a 24-bit size field and always
did, so nothing forced the old ceiling; something in how the packer was driven
changed. [05](05-block-codec.md)

### What compresses the `.cab` payloads?

Forty-five archives on each GameCube disc and fifty-three on the PlayStation 2
disc wear a Microsoft Cabinet header that no cabinet reader can open, and hold
one member each at roughly 2.4× to 4.5× compression. The payloads are **not**
block-codec streams — a full scan of every `.cab` finds no header that decodes
— and they are not MSZIP, LZX or Quantum, because the folder record says
"stored" and the sizes say otherwise. This is the largest unidentified format
on either release, and it holds most of the character art.
[04](04-executables-and-tools.md),
[`reports/gc-cab-payloads.txt`](../reports/gc-cab-payloads.txt)

### Why is 16% of the PlayStation 2 disc empty?

334,978 sectors, 686 MB, almost all of it one hole between LBA 577,224 and LBA
900,000. The seek-separation reading in [03](03-the-playstation-2-disc.md) is
plausible and unproven; so is the reading that the layout was inherited from a
plan for more content. *Tales of Destiny 2*, same publisher, two years earlier,
left 278 sectors.

---

## Measured badly

### The cross-architecture comparison does not work

`tools/xarch.py` maps instructions to what they do and compares the sequences,
so that a PowerPC routine can be compared with a MIPS one. On the real pair it
scores 16.5%; on an arbitrary unrelated routine from the same executable it
scores 16.5% and 18.5%. **The measurement has no discriminating power at this
granularity** and the tool is committed with its controls printed so that this
is visible rather than buried. [06](06-decoder-lineage.md)

What would work is not obvious. Comparing basic-block structure, or the
sequence of *loop trip counts* and constants rather than instructions, might
survive a change of instruction set; neither has been tried.

### The duplication figure is at file level, and the corpus's are not

[07](07-duplication.md) reports 36.0% for the GameCube pair and 0.1% for the
PlayStation 2 disc, hashing whole files. *Eternia* (2000) reports 50.6% and
*Destiny 2* (2002) reports 47.2%, hashing **codec blocks inside archives** —
a much finer unit. The GameCube-against-PlayStation-2 comparison is sound
because both sides are measured the same way; the comparison against 2000 and
2002 is not, and is not made.

Redoing this at block level would need the `.cab` payload format
([04](04-executables-and-tools.md)) and the `.afs` and `.d` archive layouts,
none of which are read here. It would probably raise both figures, and the
interesting question is whether it raises them by the same amount.

### The reconstructed padding is unverified

`tools/rvz.py` re-implements the lagged Fibonacci generator from the state RVZ
stores, and produces images whose SHA-1s are
`1e469f31c7b1529a769df82638056b4eabd04503` and
`c0b347d99ee3d55b7d1f14740b9062bc2c54a4ab`. The literal bytes are certainly
right — they are stored. The 90.5 MB and 67.1 MB of padding are a
reconstruction that nothing available here could check against a known hash of
the retail image. Every claim in this repository is about literal bytes;
nothing reads padding. Checking those two hashes against a preservation
database would settle it in a minute and has not been done.

---

## Unmeasured

* **`/BTL/BTLenemy.dat`.** 78 MB, 251 blocks, decoding to 140 MB — the single
  largest use of the codec on either release, and its contents are not parsed
  here at all. The PlayStation 2's file of the same name is 47.8 MB and
  contains **no** blocks, scanned at four-byte alignment across the whole file.
  What compresses it in 2004 is not identified, and is probably the same thing
  that compresses the `.cab` payloads.
* **The PlayStation 2 block census is bounded, and says so.** `census.py` gives
  up on a file after a stated budget of attempted decoder output, because the
  2004 field and root data produce enough false headers to make an exhaustive
  scan take hours. Every abandoned file is named in the report. The GameCube
  discs never reach the budget; the PlayStation 2 volumes do, so the 2004
  figures are a floor, not a total.
* **The `.d` archives.** `/d.d` is 22 MB and there are fifteen more. The first
  word looks like a header size that doubles as an offset-table length, which
  is a shape the 1997 and 2000 titles also used, but this is untested.
* **The `HVQM4` streams.** Eleven files under ten names — 231,496,801 bytes on
  disc 1 and 270,155,177 on disc 2 — played by `HVQM4PlayerEx.c` against
  `HVQM4 1.5`. Nothing here opens one, which is also why the two encodes of
  `op.h4m` can be compared only by size.
* **What `m_` and `r_` mean.** Six of the eight `.rel` modules are unreachable
  and they come in four flavours: plain, `m_`, `r_`, and `D`. `r_` is what
  ships and `D` is the debug build; `m_` is byte-different from plain at
  identical length and identical string count, which is a very specific kind of
  difference and is not explained. [09](09-leftovers.md)
* **The other 125 absent names.** [09](09-leftovers.md) accounts for the
  interesting ones. Seventeen absent skits, eight absent battle events and
  twelve absent `CHU_I` maps are listed and not investigated.
* **Whether `BTLrutee.bin` is a *Tales of Destiny* model.** It is 669,408
  bytes declared, the same order as every other character archive, and it is
  compressed with whatever the `.cab` payloads use — so it cannot be decoded
  here. If the `.cab` format is ever read, this file answers the question by
  itself. [09](09-leftovers.md)

---

## Carried back to the corpus

Three results from this pipeline belong in
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc)
rather than here, and section 8 there has been updated with them:

1. The format reached a **big-endian** console and the nine-byte header did not
   turn round.
2. The decoder's source was **edited between 2002 and 2004**, for the first
   time since 1997 — the first negative result in the "same source" chain.
3. The **opcode-sequence method does not cross instruction sets**, which bounds
   how far the corpus's own strongest tool can be pushed.
