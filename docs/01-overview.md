# Overview

*Tales of Symphonia* shipped twice in Japan, thirteen months apart, from the
same studio and largely the same build tree:

| | GameCube | PlayStation 2 |
|---|---|---|
| Code | `GTOJAF`, DL-DOL-GTOJ | SLPS-25400 |
| Released | 29 August 2003 | 22 September 2004 |
| Media | **two** miniDVDs, 1,459,978,240 bytes each | **one** DVD, 4,255,907,840 bytes |
| File system | Nintendo FST | ISO 9660 + UDF, then nine CRI `CVM` volumes |
| Executable | `main.dol`, 2,801,920 bytes, PowerPC Gekko | `SLPS_254.00`, 3,579,432 bytes, Emotion Engine |
| Compiler | Metrowerks CodeWarrior for PowerPC | Metrowerks `MW MIPS C Compiler (2.4.1.01)` |
| Files | 1,602 + 1,598 | 1,710 inside the `CVM`s, 13 outside |
| Bytes in files | 1,382,292,034 + 1,405,477,770 | 3,563,578,735 |
| Video | 10 `HVQM4 1.5` streams, `.h4m` | 13 Sofdec streams, `.sfd` |
| Audio | Nintendo `.snd` / `.song` | 107 CRI `.adx` |
| Block codec | **yes** — 487 blocks on disc 1 | **yes** — the decoder is in the executable four times |

This repository documents both, in one place, because the pair answers a
question neither answers alone.

---

## The three things this pair settles, and one it volunteered

### The 1995 compressor reached a big-endian console

Wolf Team's in-house LZSS has now been traced from the Super Famicom in 1995
to the PlayStation 2 in 2002 by
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc).
Every machine it had touched was little-endian, and the GameCube is not. It
also has ARAM and a DVD drive and an operating system with opinions about
loading, which is the reason the 2003 Game Boy Advance rebuild of *Phantasia*
was allowed to drop the format: the platform supplied its own decompressor.

The GameCube supplies one too. The game ignores it. `main.dol` contains the
decoder **four times** — two routines, each linked twice, byte for byte — with
the immediates `4078` and `4079` intact, the ring masked to twelve bits, the
control register refilled as `flags | 0xFF00`, and the copy loop unrolled by
exactly eight. The nine-byte block header **stayed little-endian** on a
big-endian machine, because the decoder assembles it one byte at a time and
never had a reason to care. See [05](05-block-codec.md).

### Between 2002 and 2004 somebody edited the decoder

The 2004 PlayStation 2 build runs on the same R5900 as *Tales of Destiny 2*
did in 2002, so byte equality is available again, and it is the strong test.
The answer is that there is none: **the longest run of identical bytes between
the two builds' decoders, at any alignment, is six bytes.** Compare that with
1997 against 2000, on the same CPU three years apart, where the identical
prefix was 212 bytes.

Some of that is a toolchain change. The rest is not: the 2004 build replaced
the decoder's byte-at-a-time dictionary clear with a **call to an Emotion
Engine quadword `bzero`**, and rounded the length from `4078` up to `4080` so
it would divide by sixteen. A compiler does not change a constant. See
[06](06-decoder-lineage.md).

The GameCube build, a year earlier, still clears the dictionary the way 2002
did.

### The two-disc split cost exactly one gigabyte

This is the result the pair exists to produce, because the two releases are
the same game from the same year and the number of discs is the only variable
that matters to it.

A GameCube disc cannot seek to the other spindle, so every asset a scene needs
must be physically on the disc that scene plays from. Measured at file level:

| | files | bytes | of which are a second copy |
|---|---:|---:|---:|
| GameCube disc 1 alone | 1,602 | 1,382,292,034 | 744,340 — **0.1%** |
| GameCube disc 2 alone | 1,598 | 1,405,477,770 | 744,340 — **0.1%** |
| **GameCube, both discs** | **3,200** | **2,787,769,804** | **1,003,551,093 — 36.0%** |
| PlayStation 2, one disc | 1,710 | 3,563,578,735 | 2,499,324 — **0.1%** |

**1,588 files are on both GameCube discs under the same name with the same
bytes.** Inside one disc there is almost no duplication at all, and the
single-disc release has almost none either — 0.1% on all three counts. Every
duplicated byte on the GameCube release is there because there are two discs.

The distinct content is 1,784,218,711 bytes. One miniDVD holds 1,459,978,240.
One disc was never possible; two discs cost a gigabyte. See
[07](07-duplication.md).

### And one nobody asked for: the packer, measured

Nineteen character-model files carry codec blocks under the same names on both
releases. Every one reports the **same number of blocks and the same unpacked
length** — identical input, cut at identical places — and every one packs
**larger in 2004**, by between +0.72% and +5.21%. The same 1,944,112 bytes went
in; 1,017,110 bytes came out in 2003 and 1,042,397 in 2004.

The specification has said for five titles that the packer left no trace in any
shipped image beyond its output. This is that trace: the tool was still on hand
in 2004, its block splitter was untouched, and its match search had got worse.
See [05](05-block-codec.md).

---

## And the archaeology

* A battle archive for **Rutee Katrea, the heroine of *Tales of Destiny*
  (1997)**, sitting on the retail disc between Regal and Sheena, built
  **2003-02-07** — four and a half months before every other battle archive on
  the disc. [09](09-leftovers.md)
* **Ten map files named after members of the team** — `_kanemaru.bin`,
  `_miya.bin`, `_anabuki.bin`, `_ichio.bin`, `_endo.bin`, `_nagasawa.bin`,
  `_hasetaka.bin`, `_otumoo.bin`, `_sawada.bin`, `_tanaka.bin` — named by the
  shipping executable and stripped from both discs.
* Five movies the executable can still ask for and will not get, two of them
  named **`tod2_cut.h4m`** and **`tod2_cut200.h4m`**, after a different game.
* Two test maps, 1.5 MB and 1.4 MB, that **did** ship.
* Forty-five archives wearing a **Microsoft Cabinet header** that no cabinet
  reader can open — carrying the only per-asset timestamps on either release,
  which date the whole asset pipeline from February to July 2003.
  [04](04-executables-and-tools.md)
* The source file the whole thing is compiled from is called **`top2.c`**.

---

## Documents

| Document | Contents |
|---|---|
| [02 — The two GameCube discs](02-the-two-discs.md) | RVZ, the FST, the layout, and what the padding is made of |
| [03 — The PlayStation 2 disc](03-the-playstation-2-disc.md) | A bridge disc, nine `CVM` volumes, and 686 MB of nothing |
| [04 — Executables and tools](04-executables-and-tools.md) | Two compilers, one SDK stamp, and the cabinets that are not cabinets |
| [05 — The block codec](05-block-codec.md) | The 1995 format on a big-endian machine |
| [06 — The decoder lineage](06-decoder-lineage.md) | 1995 → 2004, measured, including the measurement that failed |
| [07 — What the split cost](07-duplication.md) | The gigabyte |
| [08 — What changed in the port](08-version-differences.md) | Content the two releases do not share |
| [09 — Leftovers](09-leftovers.md) | Rutee, ten developers, and a movie from another game |
| [99 — Open questions](99-open-questions.md) | What is still unknown |
