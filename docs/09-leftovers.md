# Leftovers

Nine things on these discs that were not meant to ship, or were meant to and
then were not, in rough order of how much they say.

---

## 1. A playable character from a different game

`/BTL/BTLrutee.cab`, 298,219 bytes, on **both** GameCube discs, sitting in
`/BTL` between Regal and Sheena, exactly where the alphabet puts it.

The battle archives on this disc are named after the nine playable characters:
`BTLlloyd`, `BTLcollet`, `BTLgenius`, `BTLrefill`, `BTLkratos`, `BTLzelosz`,
`BTLshihna`, `BTLpresea`, `BTLregal`. Each has three to five numbered
companions. `BTLrutee` has the same shape, the same internal layout — one
member, `BTLRUTEE.BIN`, 669,408 bytes declared — and sits in the same
directory.

**Rutee Katrea is the heroine of *Tales of Destiny*, 1997.** She is not in
*Symphonia*.

The archive's own timestamp is what makes this more than a name:

```
2003-02-07 10:04:18  /BTL/BTLrutee.cab      BTLRUTEE.BIN   669408
2003-03-25 14:28:44  /mahou.cab             MAHOU.BIN       34304
2003-06-22 20:52:56  /BTL/BTLzelosz.cab     BTLZEL~1.BIN   899360
2003-06-23 12:16:48  /BTL/btllloyd.cab      BTLLLOYD.BIN   953568
...
2003-07-24 12:38:36  /BTL/BTLgenius003.cab  BTLGEN~4.BIN   771200
```

**Every other battle archive on the disc was built between 22 June and 24 July
2003. `BTLrutee.cab` was built on 7 February — four and a half months
earlier**, and never rebuilt. It is not merely unused; it stopped being part of
the pipeline while the pipeline was still running, and nobody deleted it.

The executable knows more about her than the disc does. `main.dol` names
`BTL/BTLrutee001.cab` and `BTL/BTLrutee002.cab` (absent), `npc_rutee.bin`
(absent), and four animation files `rut_02.anm`, `rut_03.anm`, `rut_08.anm`,
`rut_09.anm` (all absent). A whole character's asset set is spelled out; one
file of it survives.

The port did delete it. There is no `BTLRUTEE.CAB` on the PlayStation 2 disc.

> **Claim status.** *Verified*: the file, its size, its timestamp, its absence
> from the 2004 disc, and the seven absent names in `main.dol`. *Consistent*:
> that "rutee" refers to *Tales of Destiny*'s Rutee Katrea. Nothing on the disc
> says so; the reading rests on the name appearing in a list of playable
> characters, in a series whose previous titles this codebase is directly
> descended from.

---

## 2. Ten map files named after the team

`main.dol` carries the map table as plain text. Ten of its entries are personal
names, and all ten are absent from both discs:

```
_kanemaru.bin   _miya.bin      _anabuki.bin   _ichio.bin
_endo.bin       _nagasawa.bin  _hasetaka.bin  _otumoo.bin
_sawada.bin     _tanaka.bin
```

Four of them — `_kanemaru`, `_miya`, `_anabuki`, `_ichio` — sit in the table
immediately after `testmap.bin`, which is also absent; the other six are a
little further along. A personal scratch map each, in the shipping
executable's own list of maps, with the underscore prefix that sorts them to
the front.

And there is an eleventh entry in the same style that **did** ship:
`/MAP/_custom.bin`, 10,154 bytes. Ten people's maps were taken out and the
unnamed one was not.

This is the same shape of finding as *Venus & Braves*' seven team-named
directories on the 2002 disc — with the difference that there the directories
survived and here only the names in the table did.

---

## 3. Six module builds that cannot be loaded

Eight `.rel` files ship on each GameCube disc — Nintendo's relocatable module
format, this game's overlays:

| File | Bytes | Loadable |
|---|---:|---|
| `r_Top2Btl.rel` | 787,208 | **yes** |
| `r_Top2field.rel` | 452,844 | **yes** |
| `Top2Btl.rel` | 882,424 | no |
| `Top2BtlD.rel` | 995,888 | no |
| `Top2field.rel` | 453,756 | no |
| `Top2fieldD.rel` | 447,436 | no |
| `m_Top2Btl.rel` | 882,424 | no |
| `m_Top2field.rel` | 453,756 | no |

`main.dol` contains exactly two `.rel` names, both literal, with no format
string anywhere that could build the others:

```
0x1D4F35   relmodule is none | /r_top2btl.rel | /r_top2field.rel |
           module initialize failed | R_MultiModule.c
```

**4,115,684 bytes per disc — 8,231,368 across the set — of module builds that
the executable has no way to ask for**, against 1,240,052 bytes of the two it
can. And they are not copies of each other: all eight have distinct SHA-1s.

The debug content is not evenly spread. Counting strings that mention an
assertion, a warning, a source file or the word *debug*:

| | strings | of them debug-flavoured |
|---|---:|---:|
| `r_Top2Btl.rel` *(loaded)* | 357 | 1 |
| `r_Top2field.rel` *(loaded)* | 407 | 2 |
| `Top2Btl.rel`, `m_Top2Btl.rel` | 665 | 6 |
| `Top2BtlD.rel` | 581 | 6 |
| `Top2field.rel`, `m_Top2field.rel` | 418 | 2 |
| **`Top2fieldD.rel`** | 439 | **15** |

`Top2fieldD.rel` is the outlier and reads exactly like a build with assertions
compiled in:

```
Failed assertion pField->pSkyGTA
Failed assertion pField->pEnoData
Failed assertion pField->pSymData
Failed assertion pField->mapData[i].pMapBuff
```

The battle modules carry the source names `bt_load.c`, `bt_exec.c`,
`bt_em_bk.c`, `bt_ef_in.c`, a debug printf whose error message is misspelled —
`> DebugPrintf(...) -> Erorr!` — and a build path, which is the only one on
either release:

```
./Btl/Debug/debug
```

Four configurations of each module (plain, `m_`, `r_`, `D`) were built, and the
mastering copied all four when the loader wanted one. Then the two-disc split
([07](07-duplication.md)) copied all eight to the second disc as well.

---

## 4. Two test maps that shipped

```
0x2F25BFC0  /MAP/testfield_01.bin   1,526,511
0x2F3D0AB0  /MAP/testfield_02.bin   1,366,197
0x37731B88  /CHT/testskit.skp             864
```

2.9 MB of test map and one test skit, on the retail disc — and, being in the
duplicated set, on both retail discs. `testmap.bin` and `camtest00.cam`,
`camtest01.cam`, `camtest02.cam` are named by the executable and did not ship.

---

## 5. Five movies the player cannot see, two of them from another game

`main.dol`'s movie table has fifteen entries. Ten of them are the `.h4m` files
that shipped. Five are not on either disc:

```
MOV/pr50.h4m
MOV/pr100.h4m
MOV/sample2.h4m
MOV/tod2_cut.h4m
MOV/tod2_cut200.h4m
```

`pr50` and `pr100` read as promotional cuts at two lengths, `sample2` as
whatever the player was first tested with — and **`tod2_cut`** and
**`tod2_cut200`** are named after *Tales of Destiny 2*, the studio's own
PlayStation 2 title from the previous year, which is the game the corpus's 2002
pipeline documents. The `HVQM4` player was brought up on footage from a
different game, and the shipping table still names the test clips.

---

## 6. The source file is called `top2.c`

Of the fifteen source names in `main.dol`, one is the game itself:

```
0x2A9F60   top2.c
```

a standalone null-terminated string between a run of float constants and the
Shift-JIS word ページ. It is not an isolated slip: all eight relocatable
modules are named `Top2Btl`, `Top2field`, `Top2BtlD`, `Top2fieldD` and their
prefixed variants, and every one of those names survived into the PlayStation 2
build's own name table.

*Symphonia* is a prequel to *Tales of Phantasia*, whose internal abbreviation
throughout this series is `ToP`. The project was `Top2` and stayed `Top2` for
two years and two consoles.

---

## 7. The devkit paths shipped

`SLPS_254.00` still contains its development-host fallbacks:

```
0x22B460  cdrom0:\IOPRP300.IMG;1
0x22B480  host0:ioprp300.img
0x22B4A0  cdrom0:\IRXARC.BIN;1
0x22B4C0  host0:irxarc.bin
```

`host0:` is the PlayStation 2 devkit's path to the developer's PC. Both
fallbacks are in the retail executable, immediately after the disc paths they
back up.

---

## 8. Nine volumes still called `SAMPLE_GAME_TITLE`

Every one of the nine `CVM` volumes on the PlayStation 2 disc carries CRI's
builder defaults in its ISO 9660 volume descriptor:

```
volume id     SAMPLE_GAME_TITLE
publisher     PUBLISHER_NAME
```

Nothing reads them, so nobody filled them in. The outer disc's own volume
identifier is blank, which is probably the same story — *Tales of Destiny 2*
wrote `TOD2` there in 2002.

---

## 9. A numbering hole that survived a port

Colette's, Sheena's and Presea's battle archives are numbered `000`, `001`,
`002`, `003`, `005`. There is no `004`, on the GameCube in 2003 or on the
PlayStation 2 in 2004:

```
2003-07-16 10:39:46  /BTL/BTLcollet.cab      2004-07-22 10:39:12  /BTLCOLLET.CAB
2003-07-16 10:39:48  /BTL/BTLcollet001.cab   2004-07-22 10:39:14  /BTLCOLLET001.CAB
2003-07-16 10:39:50  /BTL/BTLcollet002.cab   2004-07-22 10:39:14  /BTLCOLLET002.CAB
2003-07-16 10:39:52  /BTL/BTLcollet003.cab   2004-07-22 10:39:14  /BTLCOLLET003.CAB
2003-07-16 10:39:54  /BTL/BTLcollet005.cab   2004-07-22 10:39:16  /BTLCOLLET005.CAB
                                             2004-07-22 10:39:16  /BTLCOLLET009.CAB
```

Whatever `004` was, it was gone before the first build in this table and the
gap was still there thirteen months later, after every archive in the set had
been rebuilt from scratch on a different console.

---

## And 127 names in total

`tools/manifest.py` lists every name the GameCube executable spells that no
file system provides: **127**, against 1,425 spelled and 3,051 present. Beyond
the ones above they include seventeen skits (`CHT/FC_B035`–`FC_B039`,
`CHT/FC_C108`–`FC_C119`), eight battle events (`BTL_EV010.SO`–`BTL_EV017.SO`),
six `CHU_T` maps, twelve `CHU_I` maps, six `PIC00*.TPL` title images, and three
`SAMPLEA/B/C.TPL`.

A handful of the 127 are artefacts of the extraction — short strings like `0.8A`
or `D.9` that happen to match a filename shape — and the report prints the
address of each so they can be told apart.

[`reports/gc-manifest.txt`](../reports/gc-manifest.txt),
[`reports/gc-cab-stamps.txt`](../reports/gc-cab-stamps.txt),
[`reports/gc-rel-modules.txt`](../reports/gc-rel-modules.txt).
