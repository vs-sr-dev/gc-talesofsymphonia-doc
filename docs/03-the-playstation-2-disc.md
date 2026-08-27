# The PlayStation 2 disc

## The volume

```
LBA 16     type 1    primary
  system id      PLAYSTATION
  volume id      (blank)
  volume space   2078080 sectors (4255907840 bytes)
  publisher      NAMCO LTD.
  application    PLAYSTATION
  created        2004081714273900$
LBA 17     type 255  terminator
LBA 18     BEA01 / NSR02 / TEA01
```

A bridge disc — ISO 9660 with a UDF descriptor sequence beside it — mastered
**17 August 2004 at 14:27:39**, twenty-five days before release. Publisher
`NAMCO LTD.`, exactly as *Tales of Destiny 2* two years earlier. The volume
identifier was left **blank**, which *Destiny 2* did not do; it wrote `TOD2`.

**One layer, and the volume says so rather than the file size.** 2,078,080
sectors is the total the primary volume descriptor declares, and a DVD-5 holds
2,295,104. The image ends where the volume says it ends, with no second-layer
descriptor and no layer break, so the disc is single layer with 217,024
sectors — 444 MB — of capacity never mastered at all.

This is worth stating plainly because the compressed distribution file is
2.86 GB and the image is not: it is **4,255,907,840 bytes**, 3.96 GiB. The two
GameCube discs together hold 2,919,956,480. The PlayStation 2 release is not
the same size as the GameCube pair — it is **45.8% larger**.

---

## Thirteen files

```
LBA         SECTORS        BYTES  PATH
279               1           57  SYSTEM.CNF
280             135       275345  IOPRP300.IMG
415            1748      3579432  SLPS_254.00
2163            135       275264  IRXARC.BIN
4000         573225   1173964800  TOSMOV.CVM
900000         1090      2232320  TOSCHT.CVM
901090       317923    651106304  TOSEV.CVM
1219013      154939    317315072  TOSCV.CVM
1373952      178288    365133824  TOSMAP.CVM
1552240       91345    187074560  TOSROOT.CVM
1643585       26492     54255616  TOSFIELD.CVM
1670077      272636    558358528  TOSSND.CVM
1942713      125125    256256000  TOSBTL.CVM
```

Two things stand out.

**The layout was placed by hand.** `TOSMOV.CVM` begins at LBA 4,000 and
`TOSCHT.CVM` at LBA **900,000**. Those are round decimal numbers, not
alignments, and nothing about ISO 9660 produces them.

**16.12% of the disc is empty**, 334,978 sectors, 686 MB — and 322,775 sectors
of it is one hole between the end of the movie volume and LBA 900,000. Compare
*Tales of Destiny 2*, on the same publisher's DVD two years earlier: **278
sectors of slack out of 1,579,104, 0.0176%**, all of it UDF structures. The
same team went from filling a disc to the sector to leaving 686 MB of it
blank, in two years, on the same console.

The gap is where the movies are separated from everything else. Reading
`TOSMOV.CVM` never requires a seek past LBA 577,224, and reading anything else
never requires a seek below LBA 900,000; the two working sets do not
interleave on the spindle. On a disc with 444 MB of unused capacity, spending
686 MB on seek separation costs nothing.

[`reports/ps2-sector-map.txt`](../reports/ps2-sector-map.txt),
[`reports/iso-volume.txt`](../reports/iso-volume.txt).

---

## `CVM`: the file system is a file system again

*Tales of Destiny 2* put its 9,206 assets in `FILE.FPB`, an archive with no
header at all, whose directory was a `u32` array compiled into the executable
that packed an extent and a padding count into the same word. Two years later
none of that survives. The 2004 build uses **CRI Middleware's `CVM`**, and a
`CVM` is a container with a small header followed by an ordinary ISO 9660
volume:

```
container            TOSROOT.CVM
file size            187074560 bytes
header size field    2036
volume size field    187074560
file system          ROFS
built by             ROFSBLD Ver.1.52 2003-06-09
volume id            SAMPLE_GAME_TITLE
publisher            PUBLISHER_NAME
created              2004081615560400$
volume space         91342 sectors
contents             197 files, 186826695 bytes
```

`CVMH` at offset 0, the container size as a big-endian word at `0x20`, then
`ROFS` and the builder's own version string at `0x34`. The ISO 9660 volume
starts at `0x1800`, three sectors in, so the primary volume descriptor lands at
`0x9800`.

Two details in that header are worth more than the format is.

**`ROFSBLD Ver.1.52 2003-06-09`** is a build-tool fingerprint — the name and
version of CRI's read-only file system builder and the date *that tool* was
compiled. It is stamped identically into all nine volumes.

**`SAMPLE_GAME_TITLE` and `PUBLISHER_NAME`** are the builder's own defaults.
Every one of the nine volumes on the retail disc still carries them: nobody ever
filled in the volume metadata, because nothing reads it. The outer volume's
identifier is blank for what is probably the same reason.

All nine volumes are stamped **2004-08-16 15:56:04** — every one, to the
second. They were not built one at a time; one run of the tool produced all
nine, the day before the disc was mastered.

| Volume | Files | Bytes |
|---|---:|---:|
| `TOSMOV.CVM` | 13 | 1,173,915,648 |
| `TOSEV.CVM` | 13 | 651,057,152 |
| `TOSSND.CVM` | 177 | 558,227,840 |
| `TOSMAP.CVM` | 497 | 364,540,192 |
| `TOSCV.CVM` | 3 | 317,265,920 |
| `TOSBTL.CVM` | 68 | 256,147,686 |
| `TOSROOT.CVM` | 197 | 186,826,695 |
| `TOSFIELD.CVM` | 256 | 53,965,314 |
| `TOSCHT.CVM` | 486 | 1,632,288 |
| **total** | **1,710** | **3,563,578,735** |

The nine volumes map one-to-one onto the GameCube's root and its eight
directories — `TOSROOT` ↔ `/`, `TOSBTL` ↔ `/BTL`, `TOSCHT` ↔ `/CHT`,
`TOSCV` ↔ `/CV`, `TOSEV` ↔ `/EV`, `TOSFIELD` ↔ `/FIELD`, `TOSMAP` ↔ `/MAP`,
`TOSMOV` ↔ `/MOV`, `TOSSND` ↔ `/S`. The port kept the shape of the file system
exactly and changed only the container.

[`reports/ps2-cvm-headers.txt`](../reports/ps2-cvm-headers.txt),
[`reports/ps2-dupes.txt`](../reports/ps2-dupes.txt).
