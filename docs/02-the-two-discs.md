# The two GameCube discs

## What arrives, and why it needs a new tool first

Both discs are distributed as **RVZ**, Dolphin's compressed disc format, which
nothing in the sibling pipelines can read. `tools/rvz.py` is the reader.
It turned out to be worth writing for its own sake, because RVZ does not merely
compress the image: it separates the image into *content* and *padding*, and
records where the boundary is.

```
container                RVZ
version                  1.0.0
compression              zstd, level 19, chunk 131072
disc type                1 (GameCube)
image size               1459978240 bytes
game id                  GTOJAF
title                    TALES OF SYMPHONIA 1
raw data entries         1
groups                   11139
```

One raw-data entry covers the whole disc, split into 11,139 groups of 128 KiB.
A group may be *packed*, meaning it is a sequence of runs that are either
literal bytes or a note saying "the next N bytes come from this generator
state". The generator is the lagged Fibonacci one Nintendo's mastering tool
used, and RVZ stores its state verbatim — seventeen big-endian words, sixty-
eight bytes per run — so no part of the seed has to be guessed.

| | disc 1 | disc 2 |
|---|---:|---:|
| Image | 1,459,978,240 | 1,459,978,240 |
| Literal bytes | 1,369,408,512 | 1,392,876,544 |
| Padding bytes | **90,569,728** | **67,101,696** |
| Padding runs with a non-zero generator state | 2,283 | 1,576 |
| SHA-1 of the reconstructed image | `1e469f31c7b1529a769df82638056b4eabd04503` | `c0b347d99ee3d55b7d1f14740b9062bc2c54a4ab` |

The padding is of **two kinds**, and the split is not decorative. Some runs
carry an all-zero generator state, which produces zeroes; the rest carry a real
state and produce the pseudo-random filler a GameCube disc is normally full of.
The first 128 KiB of the disc contains only the zero kind: the gap between the
disc header and the apploader, and the gap between the apploader and the DOL,
are plain zeroes.

> **Claim status.** The literal bytes are *Verified* — they are stored, not
> computed. The reconstructed padding is *Consistent*: the container states
> which runs are generator output and stores the state for each, and this
> repository re-implements the recurrence from that state, but no independent
> hash of the retail image was available to check the reconstruction against.
> Nothing else in this repository reads padding, so nothing else depends on it.
> See [99](99-open-questions.md).

---

## The disc header

A GameCube disc is not ISO 9660. The first `0x440` bytes are a Nintendo disc
header, the next `0x2000` are the block the apploader reads, then the
apploader itself, then the executable, then the file system: a flat array of
twelve-byte records and a string table.

| Field | disc 1 | disc 2 |
|---|---|---|
| Game code | `GTOJ` | `GTOJ` |
| Maker code | `AF` (Namco) | `AF` |
| **Disc number** | **0** | **1** |
| Version | 0 | 0 |
| Magic | `0xC2339F3D` | `0xC2339F3D` |
| Title | `TALES OF SYMPHONIA 1` | `TALES OF SYMPHONIA 2` |
| Apploader date | `2003/04/17` | `2003/04/17` |
| Apploader | 6,484 + 112,816 bytes, entry `0x81200258` | identical |
| DOL at | `0x0001F700`, 2,801,920 bytes | identical |
| FST at | `0x002CB800`, **38,564** bytes | `0x002CB800`, **38,460** bytes |
| FST max | 38,564 | **38,564** |
| Files | 1,602 in 8 directories | 1,598 in 8 directories |
| Last file ends at | 1,459,978,240 — the final byte | 1,459,978,240 |
| Bytes in files | 1,382,292,034 | 1,405,477,770 |

**The two discs were mastered together and the header proves it.** Disc 2's
own file system is 38,460 bytes, but the "maximum FST size" field on disc 2
reads 38,564 — which is disc 1's actual size. That field exists so the loader
can reserve one buffer big enough for every disc in the set, so it is written
as the maximum across the set, and it means both file systems were on the same
machine when either was written.

Everything else in the front matter is byte-identical across the two discs:
the same apploader, the same `main.dol` at the same offset, the same length.
The discs differ only in their file system and their contents.

---

## Where the space goes

```
WHAT                                      START          END        BYTES
disc header                                   0         1088         1088
disc info (bi2)                            1088         9280         8192
apploader                                  9280       128612       119332
main.dol                                 128768      2930688      2801920
FST                                     2930688      2969252        38564
1602 files                              2981888   1459978240   1382292034
```

| | disc 1 | disc 2 |
|---|---:|---:|
| Claimed by a structure or a file | 1,385,261,130 — 94.88% | 1,408,446,762 — 96.47% |
| Left over | 74,717,110 — **5.12%** | 51,531,478 — **3.53%** |
| Gaps | 388 | 387 |
| Gaps under one sector | 381 | 380 |

Almost all of the free space is a **single contiguous run** — 74.6 MB on disc 1
and 51.4 MB on disc 2 — and every other gap but six is under 2,048 bytes, which
is file-to-file alignment. Six gaps of a few kilobytes each sit in front of
`.h4m` movie files, which are aligned more coarsely than everything else
because they are streamed.

The last file on each disc ends **exactly** at 1,459,978,240. There is no tail
padding at all: the mastering tool filled the disc to its final byte.

That is the fact that makes the rest of this repository's argument work. Both
discs are 95–96% full. There was no room to move an asset from one disc to the
other to avoid copying it, and no room to fit the game on one disc. See
[07](07-duplication.md).

---

## The file system

Eight directories on each disc, and they are the same eight. Counting the
root as well:

| Directory | disc 1 | disc 2 | What |
|---|---:|---:|---|
| `/` | 171 files | 171 | character models, fonts, fixed assets |
| `/BTL` | 59 | 59 | battle |
| `/CHT` | 487 | 487 | skits (`.skp`) |
| `/CV` | 3 | 3 | voice archives |
| **`/EV`** | **8** | **5** | event scenes (`.afs`) |
| `/FIELD` | 246 | 246 | field data |
| `/MAP` | 494 | 494 | maps |
| **`/MOV`** | **6** | **5** | movies (`.h4m`) |
| `/S` | 128 | 128 | music (`.song`) |

**Seven of the nine directories are identical in both name and content.** Only
`/EV` and `/MOV` differ, and those two directories are the entire difference
between the discs. Everything else is duplicated verbatim, which
[07](07-duplication.md) measures.

Full listings: [`reports/gc-disc1-files.txt`](../reports/gc-disc1-files.txt),
[`reports/gc-disc2-files.txt`](../reports/gc-disc2-files.txt),
[`reports/gc-layout.txt`](../reports/gc-layout.txt),
[`reports/rvz-disc1.txt`](../reports/rvz-disc1.txt),
[`reports/rvz-disc2.txt`](../reports/rvz-disc2.txt).
