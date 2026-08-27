# What the two-disc split cost

This is the measurement the pair of releases exists to make. Same game, same
studio, thirteen months apart, and the number of discs is the only variable
that changes what the layout is allowed to do.

A GameCube drive reads one disc. Every asset a scene needs must be physically
on the disc that scene plays from, because there is no seeking to the other
spindle and no asking the player to swap in the middle of a battle. So
anything both halves of the game use has to be written twice.

The single-disc PlayStation 2 release does not pay that, and is the control.

---

## The numbers

`tools/dupes.py` hashes every file in each file system, whole, in place. Two
files with the same SHA-1 are the same file however they are named.

| | files | bytes | distinct bytes | a second copy |
|---|---:|---:|---:|---:|
| GameCube disc 1 alone | 1,602 | 1,382,292,034 | 1,381,547,694 | 744,340 — **0.1%** |
| GameCube disc 2 alone | 1,598 | 1,405,477,770 | 1,404,733,430 | 744,340 — **0.1%** |
| **GameCube, the set** | **3,200** | **2,787,769,804** | **1,784,218,711** | **1,003,551,093 — 36.0%** |
| PlayStation 2, one disc | 1,710 | 3,563,578,735 | 3,561,079,411 | 2,499,324 — **0.1%** |

Read that column downward. **Inside a single disc there is essentially no
duplication — 0.1% — and the single-disc release has essentially none either,
also 0.1%.** The 36.0% appears only when the two GameCube discs are put
together, and it is 1,003,551,093 bytes: **one gigabyte, to the third significant
figure.**

Duplication within one disc, on either release, is nine small assets copied for
convenience:

```
      WASTED  COPIES         EACH  FIRST
      456192       2       456192  /fontb1.dat
      179200       6        35840  /sym_angel.bin
       82944       2        82944  /dep_fontb0.dat
        8896       2         8896  /pic000.tpl
        7260       5         1815  /btl_ev005.so
        3960      11          396  /S/bgm_c016.song
        2816      23          128  /CHT/FC_B034.skp
        2784      30           96  /CHT/FC_B022.skp
         288       2          288  /CHT/FC_U092.skp
```

A font under three names, an effect under six, and a handful of 96-byte skit
stubs. That is what ordinary duplication looks like on these discs: 744 KB.

---

## What is on both discs

```
between tos-gc-d1.gcm and tos-gc-d2.gcm
  distinct contents on both      1,514
  bytes on disc 1 that are also on disc 2   1,002,806,753  (72.5%)
  bytes on disc 2 that are also on disc 1   1,002,806,753  (71.3%)

  same path on both discs        1,589
    identical content            1,588  (1,002,806,753 bytes)
    different content                1
  only on disc 1                    13 files,  269,179,676 bytes
  only on disc 2                     9 files,  333,440,955 bytes
```

**1,588 files are on both discs under the same path with the same bytes.**
Out of 1,602 and 1,598. Twenty-two files in total are unique to one disc or the
other, and one file appears on both with different contents.

That last one is the opening movie:

| | disc 1 | disc 2 |
|---|---:|---:|
| `/MOV/op.h4m` | 110,305,605 | 69,230,062 |

Two different encodes of the opening, one per disc — 41 MB shorter on disc 2,
which is the disc with less room. The opening plays from whichever disc is in
the drive, so it had to be on both, and on the disc that could not afford the
full version it was re-encoded rather than dropped.

The twenty-two files that are genuinely per-disc are exactly the event scenes
and the movies:

| Only on disc 1 | bytes | Only on disc 2 | bytes |
|---|---:|---|---:|
| `/EV/sce_001_009.afs` | 14,342,144 | `/EV/sce_084_090.afs` | 13,783,040 |
| `/EV/sce_011_020.afs` | 7,370,752 | `/EV/sce_091_100.afs` | 20,463,616 |
| `/EV/sce_021_030.afs` | 20,826,112 | `/EV/sce_101_110.afs` | 36,399,104 |
| `/EV/sce_031_040.afs` | 19,337,216 | `/EV/sce_111_120.afs` | 20,185,088 |
| `/EV/sce_041_050.afs` | 22,636,544 | `/EV/sce_121_132.afs` | 41,684,992 |
| `/EV/sce_051_060.afs` | 19,941,376 | `/MOV/as2.h4m` | 28,191,454 |
| `/EV/sce_061_070.afs` | 21,606,400 | `/MOV/as3.h4m` | 141,353,314 |
| `/EV/sce_071_083.afs` | 21,927,936 | `/MOV/s09.h4m` | 16,157,105 |
| `/MOV/as1.h4m` | 64,464,081 | `/MOV/s10.h4m` | 15,223,242 |
| `/MOV/s01.h4m` | 23,593,525 | | |
| `/MOV/s03.h4m` | 8,601,361 | | |
| `/MOV/s07.h4m` | 8,479,315 | | |
| `/MOV/s08.h4m` | 16,052,914 | | |

The scene archives are numbered `001` to `132` and the cut is between scene 83
and scene 84 — a single point in the story, one file boundary. Everything else
on both discs is the same bytes.

**Including the voice.** `/CV/cht_disc_1.afs` (81,887,232 bytes) and
`/CV/cht_disc_2.afs` (51,759,104) are *both on both discs*, names and all. The
files are named after the discs they belong to, and neither disc got to leave
the other one's copy out.

So are all 487 codec blocks ([05](05-block-codec.md)), all 45 `.cab` archives
([04](04-executables-and-tools.md)), all 487 skits, all 494 maps, both fonts,
the whole soundtrack, and all eight `.rel` modules including the six that
cannot be loaded ([09](09-leftovers.md)). The twenty largest duplicated files
alone account for 555 MB:

```
    87184096       2     87184096  /npc_all.bin
    81887232       2     81887232  /CV/cht_disc_1.afs
    77952000       2     77952000  /BTL/BTLenemy.dat
    51759104       2     51759104  /CV/cht_disc_2.afs
    36655104       2     36655104  /BTL/btlvoice.afs
    30554112       2     30554112  /BTL/BTLmagic.dat
    26220512       2     26220512  /BTL/BTLbg.dat
    22466880       2     22466880  /d.d
    13176414       2     13176414  /tos_ending.adx
    10321920       2     10321920  /BTL/BTLwin.bfp
```

---

## Was there a choice?

No, in both directions, and the disc layout in [02](02-the-two-discs.md) is
what proves it.

**One disc was impossible.** The distinct content is 1,784,218,711 bytes. A
GameCube miniDVD holds 1,459,978,240. The game overruns a single disc by
324,240,471 bytes — 22% — before a single byte is duplicated.

**Two discs left no slack to trade with.** Disc 1 is 94.88% full and disc 2 is
96.47% full; the free space is 74.7 MB and 51.5 MB, and the last file on each
disc ends on the disc's final byte. There was no room to move a shared asset
onto one disc and let the other reach across, even if the hardware had allowed
it.

So the split was forced, and once forced it cost **1,002,806,753 bytes — 56.2%
of the game's actual content, written a second time.** The two discs together
hold 2,919,956,480 bytes of capacity and deliver 1,784,218,711 bytes of game.

---

## The control, and a caveat about comparing it

The PlayStation 2 release carries **3,563,578,735 bytes across 1,710 files and
duplicates 2,499,324 of them — 0.1%.** Same team, same assets, thirteen months
later, one disc: the duplication vanishes. It is not that the studio became
tidier; it is that the constraint went away.

> **A caveat, because the corpus's earlier numbers are not this number.**
> *Eternia* (2000) reports 50.6% duplication and *Destiny 2* (2002) reports
> 47.2%, and those are **codec blocks inside archives**, hashed one packed
> stream at a time — a much finer unit than a file. The measurement here is at
> **file** level, which is the right unit for a question about what has to sit
> on which spindle, and which is not comparable with those two figures.
>
> What *is* comparable is GameCube against PlayStation 2, because both sides of
> that comparison are measured the same way, on the same game, in the same
> repository, by the same tool. That comparison is 36.0% against 0.1%.
>
> The finer measurement is left open. See [99](99-open-questions.md).

---

## What this says about *Eternia*

*Tales of Eternia* shipped on three PlayStation CDs in 2000 and the corpus
recorded 50.6% of its archive bytes as copies, reading that as the price of a
multi-disc release. This measurement supports that reading and sharpens it,
because here the two halves of the price can be told apart:

* duplication that a **single** disc also has — 0.1% here, at file level;
* duplication that exists **only because there is more than one disc** — 36.0%
  here, and 0.0% on the one-disc release of the same game.

On this pair the second is three hundred times the first. Whatever the
corresponding split is on *Eternia*'s three CDs, it is now a question that can
be asked, because it now has a shape.

[`reports/gc-dupes.txt`](../reports/gc-dupes.txt),
[`reports/ps2-dupes.txt`](../reports/ps2-dupes.txt),
[`reports/gc-layout.txt`](../reports/gc-layout.txt).
