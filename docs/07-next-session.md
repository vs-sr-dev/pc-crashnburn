# Next session: past Select Character -- the cel engine's next bits, and messages checked

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, plays the Crystal Dynamics
logo movie, draws its choice dialog, and -- with the kernel's messages and
the event broker in the runtime (session 11, `03-executables.md`, "The
pad") and a pad scheduled on `pfboot`'s command line -- takes CRASH'N BURN,
plays the intro movie, shows the Select Game menu (the real game's, the
user confirmed), and with a second A the Select Character screen. A third
A (field 4900) stops the run in the cel engine: the next screen's first
cel has PRE0's BGND bit.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 [--trace 2] [--lenient] [--disc DIR]
build/recomp-build/pfboot build/disc/launchme --max-calls 80000 --pad a@1300x1 --frames DIR  # to the menu
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 3000000 --pad a@1300x1 --pad a@4600x1 --pad a@4900x1
                                                                # to the stop, in 4 seconds
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before (and after)
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Tasks/eventbroker eventbroker.bin   # linked at 0
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin         # linked at 0x10000
```

**Always give `--max-calls`**: the game waits on the pad, on the dialog
and on every menu, for ever. With the trace on it writes about 6 MB a
second; `--trace 0` with `--frames` is the quick way through. Field
numbers in `--pad` are `gf_VBLNumber`'s: the dialog is up from field 1197,
the menu from 4478, Select Character from 4642.

## The work, in order

1. **PRE0's BGND bit** (0x40000000; `PRE0_LITERAL` is 0x80000000): the
   cel at 0x63174, 16 bpp uncoded, PRE0 0x40000bd6, at (28, 55), drawn
   right after the A on Select Character (call ~34,009 of that run). Read
   what it does in the Graphics Programmer's Guide (chapters 3 and 5:
   "The BGND Flag", the decoder's 000 value) and in Opera's MADAM where
   the guide is silent, model it in `pf_cel.cpp`, and go on screen by
   screen -- the track select, then the race, where non-square cels (the
   projector's fill rule) are sure to come.
2. **The kernel's messages on the 1993 code**: a `pfcheck` replay of
   `SendMsg`, `ReplyMsg`, `GetMsg` and `CreateSizedItem` of a port and a
   message on os_code itself (0x184d0, 0x186b8, 0x18bd4, 0x18418,
   0x1898c), as the memory and Graphics calls are replayed. It needs the
   kernel's `CheckItem` and `LookupItem` stood in for (the runtime's item
   table is the host's), its interrupt switches (0x106fc, 0x10720), and
   `SendSignal` (0x19d40) traced rather than run. The game's calls 230 to
   239 and 402 are the snapshots to take. A kit Python change: the battery.
3. Then, with the user: the display (an SDL3 window, the keyboard as the
   pad) or the sound, now that the game can be played through.

## Keep in mind

* **Messages** (`3dokit/runtime/pf_msg.cpp`): os_code's; word +0x34 of a
  message is its holder; ports of the OS's own (`pf_msgport_new`) hear a
  message through a native function, and what they take they hold
  themselves (holder 0). `CompleteIO` with a reply message still stops.
* **The event broker** (`pf_event.cpp`): the disc's, at its message
  boundary -- `EB_Configure` only (other flavours stop), the Control Pad
  only (pod 1, position 1, generic 1), a `cr_QueueMax` of 1 to 20 stops
  (the 1993 broker's word store over its byte fields). The game is an
  `LC_Observer` (trigger `ControlButtonUpdate`, `MouseUpdate`,
  `MouseMoved`) and polls through `GetJoystick` every seven fields.
* **The pad** (`pfboot --pad BUTTONS@FIELD[xN][/E]`): N presses (4 by
  default) every E fields (30), each held 6 fields; buttons up down left
  right a b c start x l r, joined by +; `--pad` may repeat.
* **Item numbers** moved by one at the boot (the broker's port is item
  10); the Graphics snapshots after the 229th call are now calls 626,
  627, 645, 2101, 2104 (the input library makes eleven more calls).
* **The cel engine** (`3dokit/runtime/pf_cel.cpp`): the guide's model
  (`D:/Homebrew6/refs/3do-devkit/docs/3dosdk/ppgfldr/ggsfldr/gpgfldr`,
  chapters 3 and 5), Opera's MADAM read where it is silent. Draws only
  square cels (HDX 1, VDY 1, HDY, VDX, HDDX, HDDY 0, the origin on a whole
  pixel). Stops on: the fill rule for anything else, SKIPX, LRFORM,
  uncoded 8 bpp, PXOR, USEAV, PIXC MS 10/11 (the guide's chapter 5 has
  their bits the wrong way round; chapter 3 and Opera agree: the top three
  bits multiply, the low two divide), TWD, a cel without both ACW and
  ACCW, POVER 01, B15POS 10, a read width unlike the write width, and
  PRE0's LITERAL and BGND bits. CFBDSUB is not modelled (nor in Opera).
  The guide's PIXC table labels P-mode 0 as the high half; hardware.h
  (and the code) put it in the low half.
* **The engine's registers persist** from cel to cel and call to call, as
  the hardware's; a cel without YOXY starts below the last one (Opera).
* **What `--frames` shows** (`pf_graphics.cpp`): the VDLs' field, the VIRS
  line first, the CLUT, the line pairs, 320 wide; not the display control
  words. Phoenix's shots sit at a scale of about 3.000 x 2.876.
* **Audio**: the attachments' states are the folio's, but nothing plays,
  so a one-shot sample never ends -- its attachment stays "playing" until
  its instrument stops. When the game starts asking whether a sound has
  finished, the sample's end (the FIFO's interrupt, 0x6578) needs a time.
* **Files** (`pf_file.cpp`): still stopping: `{a|b}` alternatives,
  `FILECMD_GETPATH`, a read past a file's last block, a stream's `WaitIO`
  on a reply port; `GetDirectory` (Immercenary's `p` stops there now).
* **Items**: a deleted number is never given again; `DeleteItem(0)` and
  `CheckItem(0)` say BADITEM.
* **Time** (`pf_time.cpp`): the guest clock; `pf_at`, `pf_on_vbl`,
  `arm_poll` every 64 safe points.
* **Tasks** (`pf_task.cpp`): one host thread each, one running at a time.
* The OS's structures are the SDK headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`),
  each field checked against the 1993 code's own accesses.
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only; the
  user can also look at a field and say whether it is the real game's.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`: 51 outputs) when the kit's Python changes -- give the script
  **absolute** output directories; the self-test (`selftest
  build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs and the sixteen Graphics snapshots, calls
  0, 8, 9, 11, 12, 14, 15, 17 to 20, 626, 627, 645, 2101, 2104);
  Immercenary's `p` and OMF2097's `LaunchMe` on `pfboot`. The scripts
  live in session scratchpads, outside the repositories: session 11's
  `pfcheck.sh` (the new snapshot numbers), `traces.sh`, `sheet2.py` (a
  labelled contact sheet of `--frames` from a field on), `kdis.py` (an
  image linked at any base: `dis`, `refs`), and the unpacked `eb.bin`
  with its disassembly `eb.dis`, `os_code.bin` with `msg.dis` (the
  kernel's messages) in `fb2fbdd2-.../scratchpad`; session 10's
  `ccbwalk.py`, `packed.py`, `cmp_dialog.py`, the guide's chapters as text
  (`ch3.txt`, `ch5.txt`) and disassemblies of GRAPHIX, AUDIOFOLIO and
  launchme (`graphix.dis`, `af.dis`, `cnb.dis`) in `cfbf8bbb-.../scratchpad`;
  `battery.sh`, OMF2097's extracted ISO and the other programs' build
  (`rop-build`, which needs `cmake` again whenever the runtime gains a
  file) in `9e8e479d-.../scratchpad`. Rebuild them if gone. Commit in the
  kit, `git pull --ff-only` in the submodule, commit the port, record in
  `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* None open. (The broker, answered in session 11: in the runtime, at its
  message boundary, since the Control Port's driver is nowhere to be read.)

## Later, not next

* The projector's fill rule for stretched, turned and bent cels (Opera
  has three paths: a line, a scale, an arbitrary quad filled by scanlines),
  then the rest the cel engine stops on.
* The display: a window (SDL3) showing the fields, with the VDL's display
  control words, and the keyboard as the pad; then running in real time
  (the guest clock held back to the host's).
* The sound: native mixers for `mixer8x2`, `sampler`, `varmono8` and
  `dcsqxdhalfmono` (SDX2, the movie's sound) fed by the values the runtime
  keeps; the attachments' DSP side and the samples' ends; the audio
  folio's cues (`SignalAtTime`, `SleepUntilTime`: `_MEDPlayer`).
* The event broker's other requests (`GetListeners`, `SetFocus`,
  `GetFocus`, the pods'), the mouse and other pods, `ControlPortChange`.
* Immercenary's `p`: `GetDirectory` next.
* The File folio's other calls (directories, `CreateFile`, `DeleteFile`,
  `OpenDiskFileInDir`, `GetDirectory`); a CD's reading time.
* The kernel's quantum (its "kernel quanta" FIRQ, handler 0x1780c); item
  numbers reused as the kernel does.
* The timer's microsecond unit and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping;
  `portfolio --sites` raises on a decompressed image (its relocation list).
* The kernel's own lists (`kb_Devices`, `kb_MsgPorts`, `kb_TaskReadyQ` and
  the rest) are not filled by the runtime; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting other kinds of
  items.
