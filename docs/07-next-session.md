# Next session: after the logo movie -- the voice stopped, then the choice screen

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, makes its screens and its
mixer as the 1993 folios do, reads its sound effects into samples, and
plays its first movie -- the Crystal Dynamics logo, `EXTRA.1` -- to its
end: its own code decodes into its two screens and `pfboot --frames`
writes what the VDLs show (`03-executables.md`, "The first movie"). The
game then stops at its 14,822nd call, the first not implemented: **audio
`StopInstrument`** (SWI 0x40003) on the movie's voice.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient] [--max-calls N] [--disc DIR]
build/recomp-build/pfboot build/disc/launchme --frames DIR      # a PPM per changed field
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before and after
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Folios/AUDIOFOLIO audiofolio.bin   # linked at 0
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin         # linked at 0x10000
python -m 3dokit.rom D:/Tools/phoenix28/ph-win64/3DO/BIOS/panafz1.bin --unpack DIR
```

The build's `TDK_RUNTIME` is the kit's working tree (`D:/Homebrew6/3dokit/runtime`),
so a runtime change can be tried before it is committed. A run to the
movie's end takes about a minute.

## The calls, in the order the game makes them (`--lenient` preview)

1. **`StopInstrument`** (SWI 3, 0x1ddc) on `dcsqxdhalfmono`, whose sound
   buffer is attached and linked to itself. Read what it does to the
   instrument and to its attachments' state (the node's +0x26, signed;
   above 1 is playing). The runtime's `Attachment::started` is a stand-in
   set by `StartInstrument` for every attachment of the instrument: read
   how `StartInstrument` starts them (0x7148) and how they stop (0x7cf8,
   0x76b8), and keep the state as the folio does.
2. `LinkAttachments(at, 0)` on the stopped attachment (SWI 0x15: when not
   playing, only +0x4c cleared -- implemented; it stops the run while the
   stand-in says playing).
3. Then, by the code (not yet run): `SwapOutDCSQXD` (0x2be10) puts
   `varmono8` back on voice 0 (`DisconnectInstruments`, `DeleteItem`,
   `AllocInstrument`, `GrabKnob`, `TweakKnob`, `ConnectInstruments`, all
   implemented), probably `DetachSample` and the buffer's sample deleted
   (a sample's `ir_Delete`, 0x3d18: not yet), and `DoLogoScreen`'s dialog
   -- the choice between the game and the Preview, from
   `IntroScreen.3DO`'s cels (likely the cel engine: `DrawCels` or
   `DrawScreenCels`), waiting on the pad (`DialogInput` 0x1f148,
   `GetJoystick`; the runtime has no pad yet -- a held button confirms the
   first entry, `08-oracle.md`).

## Keep in mind

* **What `--frames` shows** (`3dokit/runtime/pf_graphics.cpp`): the field
  as the VDLs describe it, from forced-first round to it: lines with
  video DMA only (so the VIRS line comes first: the green line at the
  top), the CLUT the entries load (kept from entry to entry), the 3DO's
  line pairs, 320 wide. Not modelled: the display control words
  (interpolation, background and transparency, a pixel's bit 15), other
  widths, a relative link. A diagnostic, not the display.
* **Audio items**: the runtime keeps each item's info on the host side
  (templates, instruments, knobs, samples, attachments); the folio's
  private lists are not made. Deleting goes through the folio's
  `ir_Delete` (`pf_on_delete`): an instrument takes its knobs and
  attachments with it. A sample's info is the folio's, field for field
  (offsets in `pf_audio.cpp`). Nothing plays.
* **Files** (`3dokit/runtime/pf_file.cpp`): the disc is a host directory;
  the shell's aliases come from the disc's own scripts. Still stopping
  the run: `{a|b}` alternatives in a path, `FILECMD_GETPATH`, a read past
  a file's last block, a stream's `WaitIO` on a reply port.
* **Items**: a deleted number is never given again (the 1993 kernel reuses
  it), and the OS's memory is never freed. Whether the 1993 kernel has an
  item 0 is not read: here `DeleteItem(0)` and `CheckItem(0)` say BADITEM
  (Immercenary's `p` and the game's `FadeToBlack1` both pass 0).
* **Time** (`3dokit/runtime/pf_time.cpp`): the guest clock; `pf_at` for an
  event, `pf_on_vbl` for the blank; `arm_poll` every 64 safe points.
* **A stop inside an OS call** names the call's site (per task thread);
  outside one, `lr`.
* **A Graphics call is checked by replaying it on GRAPHIX** (`pfboot --snap
  N DIR`, then `pfcheck ... --graphix`); sixteen pass byte for byte.
* **Tasks** (`3dokit/runtime/pf_task.cpp`): one host thread each, one
  running at a time; the program at 100, the sound thread at 110/130.
* The OS's structures are the SDK headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`),
  each field checked against the 1993 code's own accesses.
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`: 51 outputs) when the kit's Python changes -- give the script
  **absolute** output directories; the self-test (`selftest
  build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs, `--memtest DIR --ops 4000 --seed 1..6`,
  and the sixteen Graphics snapshots, calls 0, 8, 9, 11, 12, 14, 15, 17 to
  20, 615, 616, 634, 2090, 2093); Immercenary's `p` and OMF2097's
  `LaunchMe` on `pfboot`. The scripts live in session scratchpads, outside
  the repositories: session 9's `traces.sh` (the three programs' traces,
  both builds rebuilt), `pfcheck.sh` (the 22 runs), `battery.sh`,
  `vdlwalk.py` (the VDL chain in a snapshot) and `sheet.py` (a contact
  sheet of `--frames`) in `20b1a9a4-.../scratchpad`; OMF2097's extracted
  ISO and the other programs' build (`rop-build`) in
  `9e8e479d-.../scratchpad`. Rebuild them if gone (`3dokit.disc
  --extract`; the lists are the ones above). Commit in the kit, `git pull
  --ff-only` in the submodule, commit the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* None open. (The logo's last frame matched Phoenix's screenshot; the
  choice screen's screenshot -- the buttons CRASH'N BURN and PREVIEWS over
  that frame -- is the reference for the dialog, `08-oracle.md`.)

## Later, not next

* The display: a window (SDL3) showing the fields, with the VDL's display
  control words; then running in real time (the guest clock held back to
  the host's).
* The sound: native mixers for `mixer8x2`, `sampler`, `varmono8` and
  `dcsqxdhalfmono` (SDX2, the movie's sound) fed by the values the runtime
  keeps; the attachments' DSP side; the audio folio's cues (`SignalAtTime`,
  `SleepUntilTime`: `_MEDPlayer`).
* Immercenary's `p`: `UnloadSample` next.
* The File folio's other calls (directories, `CreateFile`, `DeleteFile`,
  `OpenDiskFileInDir`, `GetDirectory`); a CD's reading time.
* The kernel's quantum (its "kernel quanta" FIRQ, handler 0x1780c); item
  numbers reused as the kernel does.
* The timer's microsecond unit and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping.
* The kernel's own lists (`kb_Devices`, `kb_TaskReadyQ` and the rest) are
  not filled by the runtime; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting other kinds of
  items.
