# The decoder lineage, 1995 to 2004

## Where the corpus stood

| Pair | CPU | Identical words | Longest identical run | Opcode sequence |
|---|---|---:|---:|---:|
| Destiny 1997 ↔ Eternia 2000 | R3000A ↔ R3000A | 69 / 140 | **53 words, 212 bytes** | 95.7% |
| Destiny 1997 ↔ Destiny 2 2002 | R3000A ↔ R5900 | 0 | 0 | 51.4% |
| Eternia 2000 ↔ Destiny 2 2002 | R3000A ↔ R5900 | 0 | 0 | 49.3% |

The 2002 zeros were expected and were the point: a different CPU cannot produce
identical words, so the question became whether the *source* was the same, and
half the opcode sequence with every source-chosen constant intact said it was.

*Symphonia* adds two rows, and they say opposite things.

---

## The PlayStation 2 in 2004, against the PlayStation 2 in 2002

Same console, same CPU, two years apart. Byte equality is available again,
which makes this the strong test — and the corpus has a calibrated expectation
for it, because 1997 against 2000 on one CPU three years apart produced 212
identical bytes.

`tools/xarch.py` compares the 2002 decoder at `0x0010A1B0` against all four
copies in the 2004 executable, positionally *and* at every alignment:

| B | Identical words in place | Longest identical byte run, any alignment |
|---|---:|---:|
| `SLPS_254.00 @ 0x001C93D0` | 1 / 180 | **6 bytes** |
| `SLPS_254.00 @ 0x001C9820` | 0 / 180 | **6 bytes** |
| `SLPS_254.00 @ 0x00242C5C` | 1 / 180 | **6 bytes** |
| `SLPS_254.00 @ 0x0024324C` | 1 / 180 | **6 bytes** |

Six bytes, at any alignment, against 212. **Somebody touched the code between
2002 and 2004**, which is the outcome this comparison was set up to be able to
report.

### How much of that is the toolchain

Some of it, and the honest thing is to say so before claiming the rest.
`SLPS_254.00` carries a `.comment` section reading
`MW MIPS C Compiler (2.4.1.01)`. `SLPS_251.72` carries no `.comment` at all and
no compiler string anywhere in 1.2 MB, which is what a different vendor's
linker leaves behind. A change of compiler alone would destroy byte equality
without a line of source changing.

### The part that is not the toolchain

A compiler does not change a constant, and this one did.

**2002** clears the dictionary with an inline byte loop, to 4,078:

```
0x0010A1BC  addiu    a0, zero, 4078
0x0010A1C0  addu     v1, a3, t1
0x0010A1C4  addiu    t1, t1, 1
0x0010A1C8  sb       zero, 0(v1)
0x0010A1CC  slt      v0, t1, a0
0x0010A1D4  bne      v0, zero, 0x0010A1C0
```

**2004** calls a subroutine, with 4,080:

```
0x001C93FC  addiu    a1, zero, 4080
0x001C9400  jal      0x001DF090
0x001C9404  daddu    a0, s0, zero
```

and `0x001DF090` is a quadword clear that only exists on this console:

```
0x001DF094  srl      a1, a1, 4          ; length / 16
0x001DF098  sq       zero, 0(a0)        ; R5900, 128 bits at a time
0x001DF09C  addiu    a1, a1, -1
0x001DF0A0  addiu    a0, a0, 16
0x001DF0AC  bne      a1, zero, 0x001DF098
```

4,080 is 4,078 **rounded up to a multiple of sixteen**, so that the Emotion
Engine's 128-bit store can be used. That is a hand edit to the decoder's
source, made specifically for this CPU, and it clears two bytes the 2002 code
did not — harmlessly, since both are inside the 4,096-byte ring.

The 2003 GameCube build, a year *earlier*, still clears the dictionary with a
loop, unrolled by eight with a byte-at-a-time tail, to 4,079 and 4,078. It is
2004 that departs, not 2003.

### And the 2004 build carries two different compilations of it

`SLPS_254.00` contains the decoder pair twice, as `main.dol` does. On the
GameCube the two copies are byte-identical. On the PlayStation 2 they are not
even the same length:

| | method 1 | method 3 |
|---|---:|---:|
| first copy | `0x001C93D0`, 1,104 bytes | `0x001C9820`, 768 bytes |
| second copy | `0x00242C5C`, 1,520 bytes | `0x0024324C`, 1,176 bytes |
| identical words between them | **2 / 276** | **1 / 192** |

The second copy is much more heavily unrolled — it keeps four destination
pointers live at once and interleaves their stores — while the first is close
to what the GameCube compiler produced. Two compilations of one source with
different settings is the simplest reading; two hand variants is not excluded.
The 2002 disc had the same shape of question for a different reason, its two
copies being on two different processors.

### The decoder left the I/O processor

*Tales of Destiny 2* shipped the decoder twice, once for the EE and once for
the IOP, in `FILESYS.IRX`, with the methods renumbered internally to 2 and 4.
`tools/ring_sites.py` over both of *Symphonia*'s IOP images:

```
_work/ps2/IOPRP300.IMG, mips, 68836 words scanned
no 4078 or 4079 immediate anywhere in this image.

_work/ps2/IRXARC.BIN, mips, 68816 words scanned
no 4078 or 4079 immediate anywhere in this image.
```

By section 7's own rule that is evidence of absence, not merely failure to
find. In 2004 the I/O processor runs CRI's `ROFS` reader and Namco's
`nuSound`, and decompression happens entirely on the main CPU.

---

## The GameCube in 2003, against everything

Byte equality is not available — Gekko is a PowerPC — so the question is again
whether the source is the same, and the corpus's answer for that has been
opcode-sequence similarity.

**That method does not survive a change of instruction set, and this is the
result of trying it.** `tools/xarch.py` maps every instruction to what it does
— load a byte, store a byte, add a constant, shift, compare, branch — and
compares those sequences, with a control:

```
the two routines
  A main.dol ppc @ 0x8005D6D8
  B SLPS_254.00 mips @ 0x001C9820
  action sequence            16.5% similar

control: the same A against an unrelated routine
  B main.dol ppc @ 0x80009EF4
  action sequence            16.5% similar

control: the same A against an unrelated routine
  B main.dol ppc @ 0x8000D0A0
  action sequence            18.5% similar
```

The real pair scores **the same as, or below, an arbitrary routine picked from
the same executable**. Against the 2002 build the pair scores 15.0% and the
control 6.0%, which is a nine-point margin and still far too small to carry
weight. The measure is measuring instruction-mix, not lineage; across
instruction sets, where a MIPS `lbu` and a PowerPC `lbz` and a PowerPC `lbzx`
all mean "load a byte" but the scheduling, the addressing modes and the
register pressure are entirely different, the signal is gone.

The tool is committed with the negative result attached and it prints its
controls whether you ask for them or not, because a similarity ratio without a
control is a number that cannot be wrong.

### What does carry weight

The evidence for the GameCube build is of the kind section 7 actually
prescribes, and it is much stronger than a ratio:

1. **The constants are there.** `4078` and `4079`, twelve sites, four routines,
   at the same three positions inside each routine.
2. **The source-chosen structure is there.** `flags | 0xFF00`; the ring masked
   to twelve bits; the length in the low nibble of the second token byte and
   the reference's top bits in the high nibble; the synthetic `(i, 0x00)` and
   `(i, 0xFF)` preload; the copy loop unrolled by exactly eight.
3. **The data decodes.** 487 of 487 blocks, under `tales_block.py` with no
   edits, on both discs. A wrong dictionary would still produce the right
   length — that is section 7's own warning — but a wrong *format* would not
   produce 487 length matches out of 487.
4. **The header is still little-endian**, on a big-endian machine, which no
   independent implementation would ever choose and which a straight port
   would never notice.

See [05](05-block-codec.md).

---

## The corpus table, updated

| Pair | CPUs | Identical words | Longest identical run |
|---|---|---:|---:|
| Destiny 1997 ↔ Eternia 2000 | R3000A ↔ R3000A | 69 / 140 | 212 bytes |
| Destiny 1997 ↔ Destiny 2 2002 | R3000A ↔ R5900 | 0 | 0 |
| Eternia 2000 ↔ Destiny 2 2002 | R3000A ↔ R5900 | 0 | 0 |
| **Destiny 2 2002 ↔ Symphonia PS2 2004** | **R5900 ↔ R5900** | **1 / 180** | **6 bytes** |
| **Symphonia GC 2003, copy 1 ↔ copy 2** | Gekko ↔ Gekko | 404 / 404 | **1,616 bytes** |
| **Symphonia PS2 2004, copy 1 ↔ copy 2** | R5900 ↔ R5900 | 2 / 276 | small |

Nine years, five titles, four consoles, two byte orders, and still two
dialects. What changed is not the format. What changed is that between the
2002 disc and the 2004 disc, for the first time since 1997, the decoder's
source was opened and edited.

[`reports/decoder-lineage.txt`](../reports/decoder-lineage.txt),
[`reports/ps2-4078-scan.txt`](../reports/ps2-4078-scan.txt).
