# Next session: the sound effects' samples, then the first picture

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, makes its two screens as the
1993 GRAPHIX makes them, clears them at the first two vertical blanks,
builds its mixer as the 1993 audio folio does, starts its sound thread,
sets its audio clock to 128 Hz, and reads its fourteen sound effects
through the File folio's streams, done as the console ROM's folio does them
(`03-executables.md`, "The File folio, read in the ROM"). The game then
stops at its 240th call, the first not implemented: **audio
`SetAudioItemInfo`** (SWI 0x4001b) on the first sound's sample.

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

The build's `TDK_RUNTIME` is the kit's working tree (`D:/Homebrew6/3dokit/runtime`),
so a runtime change can be tried before it is committed.

## The calls, in the order the game makes them (`--lenient` preview)

1. **`SetAudioItemInfo` on a sample** (0x2b214, `03-executables.md`,
   "What the game does with it"): `AF_TAG_WIDTH`, `NUMBITS`, `CHANNELS`,
   `FRAMES`, `BASENOTE`, `SAMPLE_RATE`, `SUSTAINBEGIN`, `SUSTAINEND`,
   `ADDRESS`, `NUMBYTES` (named from the SDK, values listed there),
   fourteen times, one sample each. Read in AUDIOFOLIO V20.19 what the
   folio checks and derives from them (the sample's defaults at 0x2c04,
   its creation at 0x3a3c, the SWI's handler; whether `SAMPLE_RATE` is
   16.16); the runtime keeps the values for a native mixer, as for the
   instruments. Its samples are made without tags so far (`create_sample`
   in `pf_audio.cpp`).
2. `$exdir/CNB/Glue/Chars.bin` and `Plate.3do` (through the streams),
   `CDIO_OpenAFile` of `$boot/bigfile` with eight IOReqs, reads polled:
   all implemented now, to be checked against the game's own reads once
   the run gets there.
3. **GRAPHIX's `SetScreenColor` (-80) and `DisplayScreen` (-160)**: the
   first picture. Up to the 1,200th call they are the only other calls
   missing. Each can be replayed on GRAPHIX with `pfcheck`, as the eleven
   earlier Graphics calls are.

## Keep in mind

* **Files** (`3dokit/runtime/pf_file.cpp`): the disc is a host directory,
  its root `/` and `$boot` (on the console `/` is the folio's root of
  filesystems and `$boot` one of them). The shell's aliases come from the
  disc's own scripts (`startopera`, `AppStartup`), read at boot and printed
  first in the trace. No FileSystem node; a File's type and unique
  identifier are 0 (the host's directory does not keep them). A read
  completes at the next safe point (a CD's reading time is not modelled),
  past a file's end with the disc's `iamaduck` fill. Still stopping the
  run: `{a|b}` alternatives in a path, `FILECMD_GETPATH`, a read past a
  file's last block, a stream's `WaitIO` on a reply port.
* **Items**: `DeleteItem` does IOReqs and devices; a deleted number is
  never given again (the 1993 kernel reuses it), and the OS's memory is
  never freed.
* **Time** (`3dokit/runtime/pf_time.cpp`): the guest clock; `pf_at` for an
  event, `pf_on_vbl` for the blank; `arm_poll` every 64 safe points.
  The kernel's quantum is not an event yet (no two equal-priority tasks
  ready so far).
* **Drivers**: a dispatch returns 1 (done: the kernel completes it and
  `SendIO` is 1), 0 (queued, or completed by the driver itself), or an Err
  (`SendIO` returns it). The File folio's driver is the last kind.
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
  **absolute** output directories (it `cd`s into the kit); the self-test
  (`selftest build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs, `--memtest DIR --ops 4000 --seed 1..6`,
  and the eleven Graphics snapshots, calls 0, 8, 9, 11, 12, 14, 15, 17 to
  20); Immercenary's `p` and OMF2097's `LaunchMe` on `pfboot`. The scripts
  live in session scratchpads, outside the repositories: the battery in
  `0fb6cb89-.../scratchpad/battery.sh`; session 8's `traces.sh` (the three
  programs' traces, both builds rebuilt) and `pfcheck.sh` (the 17 `pfcheck`
  runs) in `6b9a6967-.../scratchpad`; OMF2097's extracted ISO and the
  other programs' build (`rop-build`) in `9e8e479d-.../scratchpad`. Rebuild
  them if gone (`3dokit.disc --extract`; the lists are the ones above).
  Commit in the kit, `git pull --ff-only` in the submodule, commit the
  port, record in `10-3dokit.md`.
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
* The File folio's other calls: `OpenDiskFileInDir`, `CreateFile`,
  `DeleteFile`, directories (`OpenDirectoryItem`, `OpenDirectoryPath`,
  `ReadDirectory`, `CloseDirectory`: the folio's vectors -20 to -40),
  `GetDirectory`; a CD's reading time.
* The kernel's quantum (its "kernel quanta" FIRQ, handler 0x1780c).
* The timer's microsecond unit and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping.
* The kernel's own lists (`kb_Devices`, `kb_TaskReadyQ` and the rest) are
  not filled by the runtime; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting other kinds of
  items.
