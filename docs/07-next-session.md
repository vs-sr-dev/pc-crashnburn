# Next session: the screens

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, prints `...cnb...`, opens the
Graphics folio, gets the memory it asks for from the OS's memory lists
(checked against the 1993 kernel's own code, `03-executables.md`), and
stops at the first call not implemented: **`CreateScreenGroup`**. Phase 4
of `06-attack-plan.md` goes on: `main` to its first `DisplayScreen`, its OS
calls in the order the game's code makes them.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient]
python -m 3dokit.aif --decompress build/disc/System/Folios/GRAPHIX graphix.bin
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin   # linked at 0x10000
```

## The calls, in the order the game makes them

1. Kernel -120, `kprintf`, `ChangeDirectory("$boot")`, `FindItem` /
   `OpenItem` / `LookupItem` of the Graphics folio -- done.
2. `FindMH(gf_ZeroPage)` (through `GetMemType`, 0x2e7f4) -- done: the VRAM
   MemHdr, bank bits 0x50000000.
3. **Graphics -48 `CreateScreenGroup`** at 0x1168 (`cnbOpenGraphics`), with
   the tags `{CSG_TAG_SPORTBITS, bank bits}, {CSG_TAG_SCREENCOUNT, 2}`:
   where the run stops.

What `cnbOpenGraphics` then does with what it gets: for each screen item,
`LookupItem`, `scr_TempBitmap` (Screen +0x78), that Bitmap's `n_Item`
(+0x18) and the Bitmap itself kept; `AddScreenGroup(group, 0)` (Graphics
-104, before the loop), then per screen `EnableHAVG` (-72) and
`EnableVAVG` (-64) of its item; the first Bitmap's `bm_Width` (+0x28) and
`bm_Height` (+0x2c), `w * 2 * h` rounded up to `gf_VRAMPageSize` pages.
Then what `--lenient` shows next: the game's banks
(`InitMemoryAllocationSystem`) are the first real users of the allocator.

## CreateScreenGroup, as GRAPHIX does it

* **The user half** (the vector, GRAPHIX 0x3e44, runs in the caller's
  mode): reads the tags over defaults -- display height and screen height
  `gf_DefaultDisplayHeight` (240), 2 screens, 1 bitmap per screen, VDL
  type 4, SPORT bits 0; widths and heights default to the folio's 320 x
  240. Unless `CSG_TAG_BITMAPBUF_ARRAY` gives the buffers, it allocates
  from the task's own lists the array of buffer pointers
  (`screens * bitmaps * 4`, flags 0), then each bitmap, `w * 2 * h` bytes
  of `MEMTYPE_VRAM|MEMTYPE_CEL`, page-rounded and `|MEMTYPE_STARTPAGE|`
  the SPORT bits when there are SPORT bits. Then SWI 0x20032 with the
  caller's item array and the parsed values. (It first checks
  `IsItemOpened(task, 2)`: 2 is the real folio's item number, its
  `CREATEFOLIO_TAG_ITEM`.)
* **The supervisor half** (SWI 50: the folio's SWI table is at 0x52a0, 51
  entries, backwards like the kernel's, so SWI n is at 0x52a0 + 4 * (50 -
  n): 50 is 0x27a0): creates the ScreenGroup item (`MKNODEID(2, 1)`,
  0x201), sets `sg_DisplayHeight` (+0x2c), `sg_ScreenHeight` (+0x28),
  `sg_Add_SG_Called` (+0x50) = 0; per screen a Screen item (0x202) with
  `scr_ScreenGroupPtr` (+0x24), its VDL by type (from
  `CSG_TAG_VDLPTR_ARRAY` or built: 0x28e0 switches on the type), its
  Bitmaps. Read it to the end before writing the runtime's.
* **The structures**: `ScreenGroup`, `Screen` and `Bitmap` are where the 1.2
  header puts them (checked on the folio's stores and the game's reads).
  **`VDL` is not**: its `vdl_Flags` was "added 24-Sep-93", after this
  folio was built, so its offsets come from GRAPHIX's code. The game
  edits its VDLs itself (`AlterVDL`, 0x13e44): what it reads there is the
  VDL's format, and later the display's colours.

## Keep in mind

* **Kernel -52 `memset` and -56 `memcpy`** are done (end of session 4):
  both return the destination, and the kernel's -56 (0x1130c) copies
  backwards when the source is below the destination, so the runtime's is
  a memmove. Immercenary's `p` now runs to its 20th call (`SendIO`).
* The OS's structures are the SDK headers'
  (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`), with offsets from a
  compiler over them (`clang -target armv4-none-eabi -S` of a file of
  `offsetof`s; 1.2 and 1.3 agree), and each one used is checked against
  the 1993 code's stores or the game's reads (`--trace 2`).
* The 1993 OS answers questions the headers cannot: what a function does
  is read in `os_code` or `GRAPHIX`, unpacked by `3dokit.aif --decompress`
  (never copied; the runtime is written from the reading). When a piece of
  the runtime reimplements a kernel function closely, `pfcheck`'s way
  (replay on the kernel's own code in `armemu`) is the check.
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`), run from the submodule's commit and from the kit, compared
  byte for byte; the self-test; `pfcheck` when memory changes. OMF2097's
  ISO must be extracted first (`3dokit.disc --extract`). Commit in the
  kit, `git pull --ff-only` in the submodule, commit the port, record in
  `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc -- even a quoted one turned `\n` into real
  newlines in session 4.

## Questions for the user

* On the console (when convenient): the same start as Phoenix's?

## Later, not next

* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header): it could, with
  `unwrap`, when a battery change is due anyway.
