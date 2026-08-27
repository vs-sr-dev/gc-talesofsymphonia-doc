# What changed in the port

The 2004 PlayStation 2 release is not a re-issue. It is a port with more
content in it, and the two file systems say where the work went.

| | GameCube 2003 | PlayStation 2 2004 |
|---|---:|---:|
| Media capacity | 2 × 1,459,978,240 = 2,919,956,480 | 4,255,907,840 |
| Capacity used | 2,787,769,804 (95.5%) | 3,569,827,122 (83.9%) |
| **Distinct content** | **1,784,218,711** | **3,563,578,735** |
| Files | 3,200 entries, 1,611 distinct base names | 1,710 entries, 1,709 distinct base names |
| Base names on this release only | 94 | 155 |
| Base names on both | 1,516 | 1,516 |

**The PlayStation 2 release carries almost exactly twice the distinct content**
— 3.56 GB against 1.78 GB — on a disc that is 45.8% larger than both GameCube
discs put together. It is also the less crowded of the two: 16.1% of its disc
is empty ([03](03-the-playstation-2-disc.md)) while the GameCube pair runs at
95–96% full ([02](02-the-two-discs.md)).

---

## Formats: what was ported and what was replaced

| Extension | GameCube | PlayStation 2 | |
|---|---:|---:|---|
| `.bin` | 595 | 662 | ported |
| `.skp` | 487 | 486 | skits, ported |
| `.dat` | 247 | 241 | ported |
| `.cab` | **45** | **53** | **ported, header and all** |
| `.afs` | 17 | 19 | CRI archive, ported |
| `.d` | 16 | 15 | ported |
| `.so` | 10 | 4 | |
| `.tpl` | 16 | 0 | Nintendo textures |
| `.rel` | 8 | 0 | Nintendo relocatable modules |
| `.h4m` | 10 | 0 | `HVQM4 1.5` video |
| `.song` | 118 | 0 | |
| `.snd` | 19 | 0 | |
| `.anm` | 13 | 0 | |
| `.adx` | 1 | **107** | CRI ADX audio |
| `.sfd` | 0 | **13** | CRI Sofdec video |
| `.pbd` | 0 | **67** | |
| `.nut` | 0 | **16** | textures |
| `.abn` | 0 | 9 | |

The pattern is clean. Everything platform-specific was replaced wholesale —
Nintendo's `.tpl` textures for `.nut`, Nintendo's `.rel` modules for something
that is not a file at all, `HVQM4` video for Sofdec, `.song`/`.snd` for 107
`.adx` streams — and everything platform-neutral was carried across unchanged,
including the studio's own `.bin`, `.dat`, `.skp` and `.d`, and including the
**block codec** ([05](05-block-codec.md)).

And including the fake cabinets. The `MSCF`-headered archives described in
[04](04-executables-and-tools.md) survived the port with the same trick, the
same one-file-per-archive layout and the same MS-DOS timestamps — 53 of them
instead of 45.

The block codec is the one carried-across format that lost ground. Its decoder
is in the 2004 executable four times over and it still compresses
`BTLUSUAL.DAT` — one block on both releases — but `BTLENEMY.DAT`, which on the
GameCube is 251 blocks and the single largest use of the codec anywhere on
either disc, contains none at all in 2004. See [05](05-block-codec.md).

---

## Content the PlayStation 2 added

Eight more `.cab` archives, and they are systematic: **one `009` archive per
playable character.**

```
BTLLLOYD009  BTLCOLLET009  BTLGENIUS009  BTLKRATOS009  BTLPRESEA009
BTLREFILL009  BTLREGAL009  BTLSHIHNA009  BTLZELOSZ009
```

Nine characters, nine new archives, each around 900 KB, all written in the same
eighty-two-second batch on 22 July 2004 as the rest. The GameCube numbering
runs `000`–`003` (and `005` for Colette, Sheena and Presea); the port adds a
`009` to every one of them.

The port also has more voice (107 `.adx` against one), more textures, and
a `TOSCHT.CVM` of 486 skits against the GameCube's 487 — one fewer, not more.

---

## Content the GameCube named and did not have, that the PlayStation 2 has

`tools/manifest.py` cross-references the names spelled inside an executable
against the files that actually shipped. On the GameCube, 127 names are spelled
and absent ([09](09-leftovers.md)). Two of them are on the PlayStation 2 disc:

| Named by `main.dol` | On either GameCube disc | On the PlayStation 2 disc |
|---|---|---|
| `CHU_T06.BIN` | no | **`TOSMAP.CVM`, 88,512 bytes** |
| `CHU_T13.BIN` | no | **`TOSMAP.CVM`, 158,176 bytes** |

Two map files that the 2003 executable could still ask for and would not get,
present and correct on the 2004 disc. The table in `main.dol` names
`chu_t00.bin` through `chu_t13.bin`, fourteen maps; eight of them shipped and
**six did not** — `T04`, `T05`, `T06`, `T07`, `T09`, `T13`. The port restored
two of the six and left the other four out.

## Content the GameCube had and the PlayStation 2 dropped

One archive, and it is the most interesting file on either release:
`/BTL/BTLrutee.cab`, 298,219 bytes, on **both** GameCube discs and on **neither**
PlayStation 2 volume. See [09](09-leftovers.md).

---

## The camera format was rebuilt

The GameCube executable names `camtest00.cam`, `camtest01.cam`,
`camtest02.cam`. The PlayStation 2 executable names `camtest00.ca2`,
`camtest01.ca2`, `camtest02.ca2` — the same three test files, one version of
the format later. Neither release ships any of them.

[`reports/version-contents.txt`](../reports/version-contents.txt),
[`reports/gc-manifest.txt`](../reports/gc-manifest.txt),
[`reports/gc-cab-stamps.txt`](../reports/gc-cab-stamps.txt),
[`reports/ps2-cab-stamps.txt`](../reports/ps2-cab-stamps.txt).
