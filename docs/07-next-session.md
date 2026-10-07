# Next session: the File folio's streams, read in the ROM

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, makes its two screens as the
1993 GRAPHIX makes them, clears them with SPORT copies at the first two
vertical blanks, builds its whole mixer as the 1993 audio folio does,
starts its sound thread, takes the audio clock and sets it to 128 Hz
(`03-executables.md`, "Time"). Time runs on the guest's own clock (1 us
per safe point, a jump ahead when every task waits). The game then stops
at its 234th call, the first not implemented: **File -4
`OpenDiskStream("CNBSFX/gun.sfx", 0)`**.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient] [--max-calls N] [--disc DIR]
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before and after
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Folios/AUDIOFOLIO audiofolio.bin   # linked at 0
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin         # linked at 0x10000
python -m 3dokit.rom D:/Tools/phoenix28/ph-win64/3DO/BIOS/panafz1.bin --unpack DIR
    # DIR/0188a0_000000.bin the File folio (at 0), DIR/00a830_020000.bin the Operator (at 0x20000)
```

The ROM is the user's, read locally: nothing from it goes in git (the
kit gets our own code and the addresses, as with `os_code`).

## The calls, in the order the game makes them (`--lenient` preview)

1. **Fourteen sound effects** (`LoadSFX`, names from 0x64338, 0x17 bytes
   apart): `OpenDiskStream` of `CNBSFX/gun.sfx`, `laser`, `missile`,
   `hazard`, `ricochet`, `laserhit`, `explosion`, `taser`, `hitwall`,
   `buttonyes`, `buttonno`, `buttonhit`, `engine1`, `flamer`; what it then
   reads of each is to be seen once the first opens.
2. `Loading two universal graphics files`, and `OpenDiskStream` of
   **`$exdir/CNB/Glue/Chars.bin`** (0x135c): the File folio's aliases
   (`$exdir`, and `$boot` that the runtime's `ChangeDirectory` already
   meets). In the preview, where every call returns 0, the game prints `BAD
   READ` and `InitHardare failed` and shuts down -- which shows its
   `UninitTimer` putting the old rate back and `DisownAudioClock`.
3. The game's other file calls (`03-executables.md`, "The OS surface"):
   `OpenDiskFile`, `CloseDiskFile`, `CreateFile`, `DeleteFile`, and the
   CDIO_ functions' `SendIO` to a file's device (`CDIO_ASYNCRead`, 0x2d48).

## Reading the File folio

* The image: `0188a0_000000.bin`, linked at 0 (`3dokit.rom --unpack`). Its
  tables (`03-executables.md`, "The console ROM"): 10 vectors at 0x6584
  (slot -4 `OpenDiskStream` 0x4e40, -8 `ReadDiskStream` 0x5110, -12
  `SeekDiskStream` 0x55f4, -16 `CloseDiskStream` 0x5094) and 14 SWIs at
  0x654c -- first find which way its SWI numbers run (the kernel's and the
  audio folio's run backwards).
* The streams are user-mode code over `OpenDiskFile` and IOReqs to the
  file's device (the File device, in the Operator); the runtime's disc is a
  host directory (`pf_host_path`). What a `Stream` holds is what the game
  reads of it, to be checked against its own reads.
* A replay of a File call on the folio's own code, as for GRAPHIX, would
  need the Operator's File device under it: see whether a narrower check
  (the stream structure the folio builds) is enough.

## Keep in mind

* **Time** (`3dokit/runtime/pf_time.cpp`): the guest clock; `pf_at` for an
  event, `pf_on_vbl` for the blank; `arm_poll` every 64 safe points.
  The kernel's quantum is not an event yet (no two equal-priority tasks
  ready so far). File IO completes at once; a CD's reading time is not
  modelled.
* **The Operator's devices** (timer, SPORT) are now read in the ROM;
  `SendIO` returns 1 when the driver finishes at once.
* **A Graphics call is checked by replaying it on GRAPHIX** (`pfboot --snap
  N DIR`, then `pfcheck ... --graphix`); eleven pass byte for byte.
* **Tasks** (`3dokit/runtime/pf_task.cpp`): one host thread each, one
  running at a time; a switch where the 1993 kernel makes one -- at an OS
  call's end, or where an event made a higher-priority task ready (at a
  safe point). The program runs at 100, the sound thread at 110/130.
* The OS's structures are the SDK headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`),
  each field checked against the 1993 code's own accesses.
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`: 51 outputs), run from the submodule's commit and from the kit,
  compared byte for byte, when the kit's Python changes -- give the script
  **absolute** output directories (it `cd`s into the kit); the self-test;
  `pfcheck` (the six memory runs, `--memtest DIR --ops 4000 --seed 1..6`,
  and the eleven Graphics snapshots, calls 0, 8, 9, 11, 12, 14, 15, 17 to
  20); Immercenary's `p` and OMF2097's `LaunchMe` on `pfboot`. The battery
  script, OMF2097's extracted ISO and the other programs' `pfboot` build
  (`rop-build`) live in session scratchpads, outside the repositories:
  rebuild them if gone (`3dokit.disc --extract`; the battery's list is the
  one above). Commit in the kit, `git pull --ff-only` in the submodule,
  commit the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* None open.

## Later, not next

* The audio folio's cues (`SignalAtTime`, `SleepUntilTime`: `_MEDPlayer`)
  and playback: native mixers for `mixer8x2`, `sampler`, `varmono8`,
  `dcsqxdhalfmono`, fed by the values the runtime keeps.
* Running in real time: the guest clock held back to the host's, once
  there is a window and sound.
* The kernel's quantum (its "kernel quanta" FIRQ, handler 0x1780c).
* The timer's microsecond unit and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping.
* The kernel's own lists (`kb_Devices`, `kb_TaskReadyQ` and the rest) are
  not filled by the runtime; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting items.
