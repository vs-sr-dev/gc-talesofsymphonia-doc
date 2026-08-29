# Tales of Symphonia (GameCube 2003 · PlayStation 2 2004, Japan) — structural documentation

Reverse-engineering notes on **`GTOJAF`**, the two-disc Japanese GameCube
release of Namco Tales Studio's *Tales of Symphonia* (29 August 2003), and on
**SLPS-25400**, its single-disc PlayStation 2 port (22 September 2004).

Both releases are documented here together, because the pair answers a question
neither answers alone: the same game, from the same studio, thirteen months
apart, with the number of discs as the variable.

This repository is **documentation and analysis only**. It contains no disc
image, no extracted asset, no patch and no translation. There is no porting,
BYOA or modding intent. Every number quoted was produced by running the tools
in [`tools/`](tools/) on images supplied separately, and their output is
committed under [`reports/`](reports/) so the claims can be checked without
owning the discs.

---

## TL;DR

| | GameCube 2003 | PlayStation 2 2004 |
|---|---|---|
| Media | **two** miniDVDs, 1,459,978,240 bytes each | **one** single-layer DVD, 4,255,907,840 bytes |
| Mastered | apploader stamped 2003/04/17 | volume stamped 2004-08-17 14:27:39 |
| File system | Nintendo FST | ISO 9660 + UDF, then nine CRI `CVM` volumes |
| Files | 1,602 + 1,598 | 1,710 |
| Bytes in files | 1,382,292,034 + 1,405,477,770 | 3,563,578,735 |
| Distinct content | **1,784,218,711** | **3,563,578,735** |
| Disc used | 94.88% / 96.47% | 83.9%, and **16.1% of the disc is empty** |
| Executable | `main.dol`, PowerPC, Metrowerks CodeWarrior | `SLPS_254.00`, R5900, `MW MIPS C Compiler (2.4.1.01)` |
| Block codec | **yes** — four routines, 487 blocks | **yes** — four routines, none on the I/O processor |
| Project name | `top2.c`, `Top2Btl.rel`, `Top2field.rel` | the same names survive |

### Three answers, and one the discs volunteered

**1 — The 1995 compressor reached a big-endian console, and the header did not
turn round.** `main.dol` contains Wolf Team's in-house LZSS decoder four times,
two routines linked twice each, byte for byte. Every source-chosen trait is
intact: `4078` and `4079`, the ring masked to twelve bits, `flags | 0xFF00`,
the copy loop unrolled by eight, the PlayStation nibble order. **487 of 487
blocks on each disc decode under the shared reference decoder with no edits and
no GameCube branch.** And the nine-byte block header is still **little-endian**
on a big-endian machine — the decoder assembles it a byte at a time, so it
never had a reason to notice. [→ 05](docs/05-block-codec.md)

**2 — Between 2002 and 2004, somebody edited the decoder.** The 2004
PlayStation 2 build runs on the same R5900 as *Tales of Destiny 2* did in 2002,
so byte equality is available and is the strong test. **The longest identical
byte run between the two, at any alignment, is six bytes** — against 212 bytes
for the 1997/2000 pair on one CPU three years apart. Part of that is a
toolchain change. The rest is not: the 2004 build replaced the decoder's inline
byte-loop dictionary clear with a call to an **Emotion Engine quadword
`bzero`**, rounding the length from `4078` up to `4080` so it divides by
sixteen. A compiler does not change a constant. The 2003 GameCube build, a year
earlier, still clears it the 2002 way. [→ 06](docs/06-decoder-lineage.md)

**3 — The two-disc split cost one gigabyte, and the single-disc release proves
it was the split.**

| | files | bytes | a second copy |
|---|---:|---:|---:|
| GameCube disc 1 alone | 1,602 | 1,382,292,034 | 744,340 — **0.1%** |
| GameCube disc 2 alone | 1,598 | 1,405,477,770 | 744,340 — **0.1%** |
| **GameCube, the set** | **3,200** | **2,787,769,804** | **1,003,551,093 — 36.0%** |
| PlayStation 2, one disc | 1,710 | 3,563,578,735 | 2,499,324 — **0.1%** |

**1,588 files are on both GameCube discs under the same path with the same
bytes.** Duplication inside a single disc is 0.1%, and on the single-disc
release it is also 0.1%; the 36.0% exists only because there are two discs. The
game's distinct content is 1,784,218,711 bytes against a miniDVD's
1,459,978,240, so one disc was impossible — and both discs run 95–96% full with
their last file ending on the final byte, so there was no slack to trade. The
split was forced, and it re-recorded **56.2% of the game**. Only twenty-two
files are genuinely per-disc: the event scenes, cut between scene 83 and scene
84, and the movies. Even the voice archives named `cht_disc_1.afs` and
`cht_disc_2.afs` are both on both discs. [→ 07](docs/07-duplication.md)

**And a fourth, which was not one of the questions.** Nineteen character-model
files carry codec blocks under the same names on both releases. All nineteen
report the **same number of blocks and the same unpacked length** — identical
input, cut at identical places — and all nineteen pack **larger in 2004**, by
between +0.72% and +5.21%; 1,017,110 bytes in 2003 against 1,042,397 in 2004
for the same 1,944,112 bytes of data. The corpus has said for five titles that
the packer left no trace beyond its output. This is that trace: it was still
being run in 2004, its block splitter was untouched, and its match search had
got worse. [→ 05](docs/05-block-codec.md)

### And the archaeology

A battle archive for **Rutee Katrea, heroine of *Tales of Destiny* (1997)**,
shipped between Regal's and Sheena's, built **2003-02-07** — four and a half
months before every other battle archive on the disc, and deleted for the port.
**Ten map files named after members of the team**, spelled by the shipping
executable and stripped from both discs, with an eleventh, `_custom.bin`, that
survived. **Six of the eight relocatable modules cannot be loaded** — 4.1 MB per
disc, 8.2 MB across the set, including a debug build carrying its assertions and
the only build path on either release, `./Btl/Debug/debug`. Movies named
**`tod2_cut.h4m`** after a different game. Two test maps totalling 2.9 MB that
did ship. Forty-five archives wearing a **Microsoft Cabinet header** that no
cabinet reader can open, carrying the only per-asset timestamps on either
release. And nine `CVM` volumes still called `SAMPLE_GAME_TITLE`.
[→ 09](docs/09-leftovers.md)

**And a fifth, five years later.** The direct sequel — *Tales of Symphonia:
Ratatosk no Kishi*, Wii, 2008 — runs on the same PowerPC 750 family and is the
first build in the corpus on which the strong byte test can be run **across a
console generation**. 872 bytes of this disc's decoder score **10 bytes** in it,
against **10** and **12** for two unrelated Wii titles — while the two
executables share **835 contiguous identical bytes** of Nintendo SDK code that
neither control has. The codec did not cross. **The `.cab` compressor did**:
`5b 80 80 8d` sits at offset `+8` of 545 of 545 payloads here and 1,506 of
1,506 there. [→ 06](docs/06-decoder-lineage.md)

**And a sixth, six years later, which is where this disc's decoder turns up
again.** *Tales of Graces* (Wii, 10 December 2009) is the second build in the
corpus on that machine and it **carries the codec** — one `4078` and one `4079`
in two routines over 1,205,688 PowerPC instruction words, both of them the 1997
shape entire. It is Metrowerks PowerPC like this disc, so the strong test has a
denominator, and it returns the largest directed result this corpus has
measured across a console generation:

| 872 bytes of this disc's decoder, whole-file, any alignment | Run |
|---|---:|
| **Tales of Graces, Wii 2009** | **138 bytes** |
| Ratatosk no Kishi, Wii 2008 | 10 |
| *The Last Story*, Wii 2011 — control | 12 |
| *Crystal Bearers*, Wii 2009 — control | 10 |
| the Graces disc's own apploader — control | 7 |
| *Tales of Xillia*, PlayStation 3 2011 — a fifth haystack, added later | **8** |

The last row comes with a caveat that makes it a non-result rather than a
negative, and it is the reason it is worth printing anyway. On that build a
*control* needle — 872 arbitrary bytes of this same `main.dol` — scores **20**,
so the decoder scores below the noise; and the whole-image ceiling between the
2009 Wii executable and that one is **96 bytes of six distinct byte values**,
`li r3,0 ; blr` repeated twelve times. Metrowerks PowerPC 32 against the
PlayStation 3 SDK's PowerPC 64 share nothing else, so byte equality was not
available and the eight means nothing.
[ps3-talesofxillia-doc](https://github.com/vs-sr-dev/ps3-talesofxillia-doc).

It is symmetric — 872 bytes of the 2009 decoder score 138 here and 8 against
every control — and `common_run.py`, handed the whole of both executables and
told nothing, ranks the decoder **first through eighth** of the 77 regions the
two builds share, pairing **all four of this disc's copies** against both of
that build's. Which of the four it descends from is therefore not decidable:
they all score the same, which is what two byte-identical pairs predict.

The 138 bytes are the **synthetic preload loop**, and unlike the 2003↔2008
comparison there is no longer a longer runtime run standing over it: the best
non-decoder region between this disc and 2009 is 107 bytes. Six years and two
SDK generations moved the C runtime; the preload loop did not move.

One correction to this repository's own instrument came out of it. Re-run with
a probe that counts `rlwimi` as well as `rlwinm` for the high-nibble
placement, this disc's structural fingerprint count gains **two** high-nibble
inserts that had been missed since it was opened.
[wii-talesofgraces-doc](https://github.com/vs-sr-dev/wii-talesofgraces-doc)

Start at [docs/01-overview.md](docs/01-overview.md).

---

## Claim status

| Claim | Status | Where |
|---|---|---|
| GameCube images are 1,459,978,240 bytes; file systems as tabulated | **Verified** | [02](docs/02-the-two-discs.md) |
| Disc 2's "maximum FST size" field carries disc 1's actual size | **Verified** | [02](docs/02-the-two-discs.md) |
| GameCube padding regions and their extent | **Verified** | [02](docs/02-the-two-discs.md) |
| The *reconstruction* of that padding's bytes | *Consistent* — no reference hash was available | [02](docs/02-the-two-discs.md), [99](docs/99-open-questions.md) |
| PlayStation 2 disc is single layer, 2,078,080 sectors | **Verified** — from the volume descriptor, not the file size | [03](docs/03-the-playstation-2-disc.md) |
| 16.12% of the PlayStation 2 disc is unused | **Verified** | [03](docs/03-the-playstation-2-disc.md) |
| …and that the hole is seek separation | *Open* | [99](docs/99-open-questions.md) |
| `CVM` layout, `ROFSBLD Ver.1.52 2003-06-09`, `SAMPLE_GAME_TITLE` | **Verified** | [03](docs/03-the-playstation-2-disc.md) |
| Four decoder routines in `main.dol`, two byte-identical pairs | **Verified** | [05](docs/05-block-codec.md) |
| 487 / 487 blocks decode under the unmodified reference decoder | **Verified** | [05](docs/05-block-codec.md) |
| The nine-byte header stayed little-endian | **Verified** | [05](docs/05-block-codec.md) |
| No decoder on either PlayStation 2 I/O processor image | **Verified** — by section 7's absence rule | [06](docs/06-decoder-lineage.md) |
| 2002 ↔ 2004: longest identical byte run is 6 bytes | **Verified** | [06](docs/06-decoder-lineage.md) |
| …that the difference is *partly* a toolchain change | *Consistent* | [06](docs/06-decoder-lineage.md) |
| …that the `4078` → `4080` quadword clear is a source edit | **Verified** — a compiler cannot change the constant | [06](docs/06-decoder-lineage.md) |
| Cross-architecture opcode similarity distinguishes nothing | **Verified negative** — the control scores the same | [06](docs/06-decoder-lineage.md), [99](docs/99-open-questions.md) |
| 19 files repack larger in 2004 at identical block count and unpacked length | **Verified** | [05](docs/05-block-codec.md) |
| …*why* the 2004 packer is worse | *Open* | [99](docs/99-open-questions.md) |
| Duplication figures, at file level | **Verified** | [07](docs/07-duplication.md) |
| …compared with *Eternia*'s 50.6% or *Destiny 2*'s 47.2% | *Not comparable* — those are block level | [99](docs/99-open-questions.md) |
| Six `.rel` modules are unreachable from `main.dol` | **Verified** — two literal names, no format string | [09](docs/09-leftovers.md) |
| `BTLrutee.cab` exists, is dated 2003-02-07, is gone from the port | **Verified** | [09](docs/09-leftovers.md) |
| …that "rutee" is *Tales of Destiny*'s Rutee Katrea | *Consistent* | [09](docs/09-leftovers.md) |
| Ten team-named maps are spelled and absent | **Verified** | [09](docs/09-leftovers.md) |
| `.cab` payloads are not block-codec streams | **Verified** — 13.6 MB scanned at every byte offset, 0 blocks | [99](docs/99-open-questions.md) |
| What the `.cab` payloads *are* | *Open* | [99](docs/99-open-questions.md) |
| Why the packer's blocks grew thirtyfold | *Open* | [99](docs/99-open-questions.md) |
| The 2003 decoder scores 10 bytes in the 2008 Wii sequel, against 835 of shared SDK code | **Verified** | [06](docs/06-decoder-lineage.md) |
| …and 10 and 12 in two unrelated Wii titles, so 10 is the noise floor | **Verified** | [06](docs/06-decoder-lineage.md) |
| The `.cab` payload compressor is the same tool in 2003 and 2008 | **Verified** — `5b 80 80 8d` at `+8` in 2,051 of 2,051 payloads | [99](docs/99-open-questions.md) |
| …what that compressor is | *Open* | [99](docs/99-open-questions.md) |

---

## Documents

| Document | Contents |
|---|---|
| [01 — Overview](docs/01-overview.md) | The two releases side by side, and the three results |
| [02 — The two GameCube discs](docs/02-the-two-discs.md) | RVZ, the FST, the layout, and what the padding is made of |
| [03 — The PlayStation 2 disc](docs/03-the-playstation-2-disc.md) | A bridge disc, nine `CVM` volumes, and 686 MB of nothing |
| [04 — Executables and tools](docs/04-executables-and-tools.md) | Two compilers, one SDK stamp, and the cabinets that are not cabinets |
| [05 — The block codec](docs/05-block-codec.md) | The 1995 format on a big-endian machine |
| [06 — The decoder lineage](docs/06-decoder-lineage.md) | 1995 → 2004, measured, including the measurement that failed |
| [07 — What the split cost](docs/07-duplication.md) | The gigabyte |
| [08 — What changed in the port](docs/08-version-differences.md) | Content the two releases do not share |
| [09 — Leftovers](docs/09-leftovers.md) | Rutee, ten developers, and a movie from another game |
| [99 — Open questions](docs/99-open-questions.md) | What is still unknown, and how to attack it |

## Tools

Dependency-free Python 3 under [`tools/`](tools/), one file per job — with one
declared exception: `rvz.py` needs the `zstandard` module, because the GameCube
images are distributed zstd-compressed. See [`tools/README.md`](tools/README.md).

```sh
python tools/rvz.py "disc1.rvz" -o disc1.gcm
python tools/gcm.py disc1.gcm --header
python tools/ring_sites.py gc1/main.dol --ppc --base 0x800056C0 --off 0x26C0
python tools/census.py --gc disc1.gcm disc2.gcm --validate Kratos.bin
python tools/dupes.py --gc disc1.gcm disc2.gcm
python tools/cab.py --gc disc1.gcm --sorted
python tools/rel.py disc1.gcm
```

`tales_block.py` is copied from
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc) and
**must not be edited here.** That it decodes a GameCube disc without
modification is the result, not an implementation detail.

## The corpus

This is the fifth title in a series of pipelines that share one specification:

| Title | Platform | Year | Uses the codec | Pipeline |
|---|---|---|---|---|
| Tales of Phantasia | Super Famicom | 1995 | yes, `$81` / `$83` | [snes-talesofphantasia-doc](https://github.com/vs-sr-dev/snes-talesofphantasia-doc) |
| Tales of Phantasia | Game Boy Advance | 2003 | **no** — BIOS `LZ77UnComp` | same |
| Tales of Destiny | PlayStation | 1997 | yes, methods 1 / 3 | [ps1-talesofdestiny-doc](https://github.com/vs-sr-dev/ps1-talesofdestiny-doc) |
| Tales of Eternia | PlayStation | 2000 | yes — the same object code as 1997 | [ps1-talesofeternia-doc](https://github.com/vs-sr-dev/ps1-talesofeternia-doc) |
| Tales of Destiny 2 | PlayStation 2 | 2002 | yes — same source, recompiled | [ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc) |
| Venus & Braves | PlayStation 2 | 2003 | **no** — on the *Destiny 2* disc | same |
| **Tales of Symphonia** | **GameCube** | **2003** | **yes — on PowerPC** | this repository |
| **Tales of Symphonia** | **PlayStation 2** | **2004** | **yes — and edited** | this repository |
| **Ratatosk no Kishi** | **Wii** | **2008** | **no** — the direct sequel, same ISA | [wii-talesofsymphoniadotnw-doc](https://github.com/vs-sr-dev/wii-talesofsymphoniadotnw-doc) |
| **Tales of Graces** | **Wii** | **2009** | **yes — 138 bytes of this disc's decoder** | [wii-talesofgraces-doc](https://github.com/vs-sr-dev/wii-talesofgraces-doc) |

The format itself is documented once, in
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc).

## Licence

Tools under [`tools/`](tools/): MIT, see [LICENSE](LICENSE).
Documentation under [`docs/`](docs/), [`reports/`](reports/) and this README:
CC BY 4.0, see [LICENSE-DOCS](LICENSE-DOCS).

`tales_block.py` carries the corpus repository's own MIT licence unchanged.
