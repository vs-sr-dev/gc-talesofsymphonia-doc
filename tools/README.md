# Tools

Dependency-free Python 3, one file per job, no imports beyond the standard
library. Nothing here bundles game data; every tool operates on an image you
supply.

One exception, declared: `rvz.py` needs the `zstandard` module, because the
GameCube images are distributed compressed with zstd and Python's standard
library does not implement it. Everything downstream of it works on a plain
`.gcm` and needs nothing.

```sh
export D1="Tales of Symphonia (Japan) (Disc 1).gcm"
export D2="Tales of Symphonia (Japan) (Disc 2).gcm"
export PS2="Tales of Symphonia (Japan).iso"
```

## Getting the images open

| Tool | What it does |
|---|---|
| `rvz.py` | Reads Dolphin's RVZ container and writes the GameCube image inside it. Also maps the disc's padding, which the container records explicitly. |
| `gcm.py` | GameCube disc: header, apploader, DOL, and the FST. |
| `iso9660.py` | ISO 9660 volume and directory walker. *Copied from `ps2-talesofdestiny2-doc`.* |
| `cvm.py` | CRI `CVM` container — a header and then an ISO 9660 volume. Reads the builder fingerprint out of the header. |

```sh
python tools/rvz.py disc1.rvz --info
python tools/rvz.py disc1.rvz -o "$D1"
python tools/gcm.py "$D1" --header
python tools/gcm.py "$D1" --list
python tools/gcm.py "$D1" --extract gc1/
python tools/iso9660.py "$PS2" --pvd
python tools/cvm.py TOSROOT.CVM --header
```

## The codec

| Tool | What it does |
|---|---|
| `tales_block.py` | **The reference decoder, copied unmodified from [tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc).** Do not edit it here; the point of this pipeline is that it decodes a GameCube disc without changes. |
| `ring_sites.py` | Finds the ring constants `4078` / `4079` in an executable, on **MIPS or PowerPC**, and reports the enclosing routine. |
| `census.py` | Scans a whole file system for blocks and checks every one against its declared length. Prints both of its bounds. |
| `decoder_lineage.py` | Compares two MIPS routines word by word and by opcode sequence. *Copied from `ps2-talesofdestiny2-doc`.* |
| `xarch.py` | Compares two routines across instruction sets, and insists on controls. **See the note below.** |
| `dismips.py` | MIPS disassembler. *Copied from `ps2-talesofdestiny2-doc`.* |
| `disppc.py` | PowerPC disassembler, enough of one to read a decompressor. |

```sh
python tools/tales_block.py --selftest
python tools/ring_sites.py gc1/main.dol --ppc --base 0x800056C0 --off 0x26C0
python tools/ring_sites.py iso/SLPS_254.00 --mips --base 0x00100000 --off 0x100
python tools/census.py --gc "$D1" "$D2" --validate Kratos.bin
python tools/disppc.py gc1/main.dol --at 0x5A088 --va 0x8005D088 44
python tools/xarch.py A.elf mips 0x0010A1B0 B.elf mips 0x001C93D0 --words 180
```

> **`xarch.py` does not work, and says so.** Its cross-architecture similarity
> score puts the real decoder pair at 16.5% and an arbitrary unrelated routine
> at 16.5–18.5%. It is committed with that result documented in
> [`docs/06`](../docs/06-decoder-lineage.md) and
> [`docs/99`](../docs/99-open-questions.md), and it prints its controls whether
> you ask for them or not, because a similarity ratio without a control is a
> number that cannot be wrong. Its *byte* comparison — longest identical run at
> any alignment — is sound and is what the 2002-against-2004 result rests on.

## The discs

| Tool | What it does |
|---|---|
| `dupes.py` | Hashes every file in a file system and reports duplication within it and between several of them. |
| `layout.py` | Where every byte of a GameCube disc goes, and every gap between. |
| `sector_map.py` | The same for an ISO 9660 image. *Copied from `ps2-talesofdestiny2-doc`.* |
| `manifest.py` | Cross-references the file names an executable spells against the files that shipped. |
| `cab.py` | Reads the `MSCF`-headered archives and their MS-DOS timestamps. |
| `rel.py` | Lists the GameCube relocatable modules and says which ones the executable can load. |

```sh
python tools/dupes.py --gc "$D1" "$D2"
python tools/dupes.py --cvm iso/TOS*.CVM
python tools/layout.py "$D1" --gaps 12
python tools/manifest.py gc1/main.dol --gc "$D1" "$D2"
python tools/cab.py --gc "$D1" --sorted
python tools/rel.py "$D1"
```

## Copied, not rewritten

`tales_block.py` is a byte-for-byte copy from
[tales-blockcodec-doc](https://github.com/vs-sr-dev/tales-blockcodec-doc).
`iso9660.py`, `dismips.py`, `decoder_lineage.py`, `ps2elf.py` and
`sector_map.py` are byte-for-byte copies from
[ps2-talesofdestiny2-doc](https://github.com/vs-sr-dev/ps2-talesofdestiny2-doc).

Keeping them identical is deliberate. A decoder that needed a patch to read a
new title would not have proved anything about the title.
