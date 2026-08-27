# Executables, and the tools that left their names

## `main.dol` — GameCube

```
NAME     FILE         ADDR               SIZE
text0    0x00000100   0x80003100         9664
text1    0x000026C0   0x800056C0      1523648
data0    0x00176680   0x80179680           32
data1    0x001766A0   0x801796A0           32
data2    0x001766C0   0x801796C0       402464
data3    0x001D8AE0   0x801DBAE0       852896
data4    0x002A8E80   0x8034B860          992
data5    0x002A9260   0x8034C680        11936
bss      0x00000000   0x802ABE80       669436
entry 0x80003154
```

2,801,920 bytes, at disc offset `0x1F700` on **both** discs, byte for byte
identical. One executable, two discs: `main.dol` never learns which disc it is
on from its own contents, only from the disc header's disc-number field.

The compiler names itself: `Metrowerks Target Resident Kernel for PowerPC`,
`Metrowerks CW runtime library initializing default heap`. Fifteen source file
names survive in assertion and error strings:

```
GCFile.c  GCSYS.c  HVQM4PlayerEx.c  R_MultiModule.c  actor.c  animPipe.c
dvd.c  dvdfs.c  main.c  mode_movie.c  mode_skit.c  scenario.c  top2.c
vi.c  window.c
```

Thirteen of those are what you would expect. `R_MultiModule.c` names the loader
for the eight `.rel` files — Nintendo's relocatable-module format, the
GameCube's answer to overlays. And **`top2.c`** is the game.

*Symphonia* is a prequel to *Tales of Phantasia*, which in Japanese is
*Teiruzu obu Fantajia*, and which every Namco internal document abbreviates
`ToP`. The main source file of *Tales of Symphonia* is named after the game it
is a prequel to, plus a `2`. It is a standalone null-terminated string, sitting
between a run of float constants and the Shift-JIS word ページ.

## `SLPS_254.00` — PlayStation 2

3,579,432 bytes, one loadable segment at `0x00100000`, 894,656 instruction
words. It carries a `.comment` section, which *Tales of Destiny 2* did not:

```
MW MIPS C Compiler (2.4.1.01)  PlayStation2
```

Metrowerks again — the same vendor on both consoles, which is worth holding on
to when reading [06](06-decoder-lineage.md), because *Destiny 2* in 2002 left
no compiler string at all and was very likely not built with it.

The two development-host paths were never taken out:

```
0x22B460  cdrom0:\IOPRP300.IMG;1
0x22B480  host0:ioprp300.img
0x22B4A0  cdrom0:\IRXARC.BIN;1
0x22B4C0  host0:irxarc.bin
```

`host0:` is the devkit's link to the developer's PC. Both fallbacks shipped.

CRI's file system sources name themselves too, in assertion strings:
`../../pfs_cvfs.c`, `../../rofs_hn.c`, `../../rofs_if.c`, `../../rofs_mai.c`,
`../../rofs_pfs.c`, `../../rofs_dir.c` — the `ROFS` half of the `CVM` reader
described in [03](03-the-playstation-2-disc.md).

## The I/O processor

`IRXARC.BIN`, 275,264 bytes, holds eight modules:

```
cri_adxi.irx  libsd.irx  mcman.irx  mcserv.irx
mtapman.irx   nuSound.irx  padman.irx  sio2man.irx
```

`nuSound` is Namco's own sound library, which *Destiny 2* also shipped.
`cri_adxi.irx` identifies itself as `CRI_ADX_Driver Ver.9.20`, built
**10 May 2004 13:11:07**, alongside `DTX Ver.1.07` and `ADXRT Ver.3010` from
the same build minute. `IOPRP300.IMG` is Sony's stock replacement kernel image,
`Kernel Ver. 2.2, Copyright 1999-2002 (C) Sony Computer Entertainment`, with
`loadelf version 3.30`.

**None of these modules contains the block codec.** See [05](05-block-codec.md);
the 2002 disc put a second copy of the decoder on the I/O processor and this
one does not.

---

## Two SDK stamps

Two components of Nintendo's SDK date themselves, in two different places on
the disc, twelve minutes apart.

In the apploader, at disc offset `0x35EC` and `0x3618`:

```
Apploader Initialized.  $Revision: 32 $.
This Apploader built Apr 17 2003 12:46:20
```

And inside `main.dol` itself, at `0x29FEE3`:

```
<< Dolphin SDK - DSP  release build: Apr 17 2003 12:34:16 (0x2301) >>
```

**17 April 2003** — four months before release, and the same date the disc
header's apploader field carries. The apploader is byte-identical on both
discs, so both were mastered from one SDK installation, and the DSP component
linked into the game came from the same one.

The GameCube's video is `HVQM4 1.5`, Hudson's codec, played through
`HVQM4PlayerEx.c`. The PlayStation 2's is Sofdec, CRI's, in `.sfd` files. Of
everything in the two builds, the video pipeline is the piece that was
replaced wholesale rather than ported.

---

## Forty-five cabinets that are not cabinets

Forty-five files on each GameCube disc, and fifty-three on the PlayStation 2
disc, begin with `MSCF` — the signature of a Microsoft Cabinet. They are not
cabinets. The header is well formed:

```
version        1.3
cab_size       119593
first_file     0x38
n_files        1
folders        [(8, 0, 0)]

EFFECT.TPL         536992  2003-07-03 12:48:28  attr 0x0020
```

— and then the folder claims **zero data blocks and no compression** while the
payload is 119,510 bytes against a declared 536,992. Nothing that reads
cabinets could open one. What is being reused is the *file entry*: a name, an
uncompressed length, and an MS-DOS date and time. The payload behind it is the
studio's own compressed stream.

Which makes these the only per-asset timestamps on either release, and they
date the asset pipeline rather than the disc:

| GameCube, 2003 | | PlayStation 2, 2004 | |
|---|---:|---|---:|
| 02-07 | **1** | 07-14 | 1 |
| 03-25 | 4 | 07-15 | 3 |
| 06-22 | 4 | 07-19 | 1 |
| 06-23 | 17 | **07-22** | **43** |
| 06-27 | 5 | 07-27 | 5 |
| 07-03 | 1 | | |
| 07-08 | 4 | | |
| 07-16 | 5 | | |
| 07-24 | 4 | | |

The GameCube pipeline ran per character over two months: Zelos on 22 June,
Lloyd, Refill, Sheena and Kratos on 23 June, Presea on 27 June, Regal on 8
July, Colette on 16 July, Genius on 24 July — each character's four or five
archives written within four seconds of one another, then nothing for a week.

The PlayStation 2 rebuilt **43 of its 53 archives in eighty-two seconds** on 22
July 2004. That is not a pipeline running per character; that is one batch over
the whole set.

And one archive on the GameCube disc does not belong to either pattern. See
[09](09-leftovers.md).

Short names give the build host away as well. Members appear as `BTLKRA~1.BIN`,
`BTLLLO~2.BIN` — MS-DOS 8.3 truncations — and four of them as `BT2581~1.BIN`,
`BT1554~1.BIN` and `BTA238~1.BIN` on the GameCube and `OEQS000~.BIN` on the
PlayStation 2, which is what Windows generates when the ordinary truncation
would collide. The asset tool ran on Windows and
opened its inputs by short name.

[`reports/gc-cab-stamps.txt`](../reports/gc-cab-stamps.txt),
[`reports/ps2-cab-stamps.txt`](../reports/ps2-cab-stamps.txt),
[`reports/ps2-iop-modules.txt`](../reports/ps2-iop-modules.txt).
