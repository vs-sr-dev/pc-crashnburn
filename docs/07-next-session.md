# Next session: the pad -- the kernel's messages and the event broker

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, plays the Crystal Dynamics
logo movie to its end, takes its sound down as the 1993 audio folio does,
and draws its choice dialog -- CRASH'N BURN lit, PREVIEWS dimmed -- on the
runtime's cel engine, matching Phoenix's screenshot (`03-executables.md`,
"The movie's end, and the choice dialog"; `08-oracle.md`). It then waits
on the pad for ever: the run no longer stops by itself.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 [--trace 2] [--lenient] [--disc DIR]
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 --frames DIR   # a PPM per changed field
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before (and after)
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Folios/AUDIOFOLIO audiofolio.bin   # linked at 0
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin         # linked at 0x10000
python -m 3dokit.rom D:/Tools/phoenix28/ph-win64/3DO/BIOS/panafz1.bin --unpack DIR
```

**Always give `--max-calls`** now: without it the dialog runs until
killed, and with the trace on it writes about 6 MB a second (session 10
filled 3.3 GB before noticing). 34,100 calls reach the dialog with both
buffers drawn (VBL 1197). `--snap` also works on a call not implemented
yet. The build's `TDK_RUNTIME` is the kit's working tree.

## The work, in order

1. **The kernel's messages, as os_code makes them.** Read in os_code
   (`os_code.bin`, linked at 0x10000; the kernel's SWI table runs
   backwards as the folios' do): MsgPort items (`CreateMsgPort` is the
   library's glue for `CreateItem` of a MSGPORTNODE: a name, a priority, a
   signal allocated when none is given), Msg items (`CreateMsg`: a reply
   port), `SendMsg` (SWI 16: the data pointer and size, the message on the
   port's list, the port's signal sent), `GetMsg` (19), `ReplyMsg` (18: the
   result, back to the reply port), `WaitPort` (the library's, or the
   kernel's), `GetThisMsg`, and what `msgport.h` says of `msg_Result`,
   `msg_DataPtr`, `msg_DataSize`, small messages. The game's input library
   (0x2e204 `InitEventUtility`, 0x2e3b8 `GetControlPad`, 0x2e530 its event
   reader) is the first user; read what it calls in order.
2. **The event broker.** The disc's `System/Tasks/eventbroker` (16,016
   bytes; started by `startopera`): read how it makes its port
   "eventbroker", answers `EB_Configure` (event.h: `EB_ConfigureReply`?),
   keeps its listeners and their focus, and reports pad changes
   (`EB_EventRecord`: an `EventBrokerHeader`, `EventFrame`s, a
   `ControlPadEventData` of button bits), and what it reads the pads with
   (`controlport.h`; the ControlPort device's driver is likely in the ROM's
   Operator, like SPORT and the timer). Then decide, with the user if it is
   not clear-cut: run the disc's broker recompiled as a task of its own, or
   do in the runtime what it does at its message boundary. The game's
   request: `LC_FocusListener`, triggers `ControlButtonUpdate`,
   `MouseUpdate`, `MouseMoved`, 0x6c bytes at 0x6a4c4.
3. **A pad for `pfboot`**: a schedule of buttons on the command line until
   there is a window -- a burst of regular presses, each pressed and then
   released (the user's choice, session 10: a held button might leave the
   game waiting for the release). Then: what the dialog does with A
   (`DialogInput` 0x1f148, `DoLogoScreen` 0x20ef0) -- the game's intro
   movie, then the Rally / Tournament / Options menu, by the code.

## Keep in mind

* **The cel engine** (`3dokit/runtime/pf_cel.cpp`): the guide's model
  (`D:/Homebrew6/refs/3do-devkit/docs/3dosdk/ppgfldr/ggsfldr/gpgfldr`,
  chapters 3 and 5), Opera's MADAM read where it is silent. Draws only
  square cels (HDX 1, VDY 1, HDY, VDX, HDDX, HDDY 0, the origin on a whole
  pixel). Stops on: the fill rule for anything else, SKIPX, LRFORM,
  uncoded 8 bpp, PXOR, USEAV, PIXC MS 10/11 (the guide's chapter 5 has
  their bits the wrong way round; chapter 3 and Opera agree: the top three
  bits multiply, the low two divide), TWD, a cel without both ACW and
  ACCW (Opera's turn test calls a square cel CCW, the guide calls a front
  face CW -- read before drawing either alone), POVER 01, B15POS 10, a read
  width unlike the write width. CFBDSUB is not modelled (nor in Opera).
  Note that the guide's PIXC table labels P-mode 0 as the high half;
  hardware.h (and the code) put it in the low half.
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
  on a reply port.
* **Items**: a deleted number is never given again; `DeleteItem(0)` and
  `CheckItem(0)` say BADITEM.
* **Time** (`pf_time.cpp`): the guest clock; `pf_at`, `pf_on_vbl`,
  `arm_poll` every 64 safe points.
* **Tasks** (`pf_task.cpp`): one host thread each, one running at a time.
  A second program (the broker, if it runs as itself) has no loader yet.
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
  `pfcheck` (the six memory runs and the sixteen Graphics snapshots, calls
  0, 8, 9, 11, 12, 14, 15, 17 to 20, 615, 616, 634, 2090, 2093);
  Immercenary's `p` and OMF2097's `LaunchMe` on `pfboot`. The scripts
  live in session scratchpads, outside the repositories: session 10's
  `traces.sh`, `pfcheck.sh`, `battery.sh`, `vdlwalk.py`, `sheet.py`,
  `ccbwalk.py` (a CCB list in a snapshot), `packed.py` (a packed cel's
  rows), `cmp_dialog.py` (a field beside Phoenix's shot), the guide's
  chapters as text (`ch3.txt`, `ch5.txt`) and disassemblies of GRAPHIX,
  AUDIOFOLIO and launchme (`graphix.dis`, `af.dis`, `cnb.dis`) in
  `cfbf8bbb-.../scratchpad`; OMF2097's extracted ISO and the other
  programs' build (`rop-build`, which needs `cmake` again whenever the
  runtime gains a file) in `9e8e479d-.../scratchpad`. Rebuild them if
  gone. Commit in the kit, `git pull --ff-only` in the submodule, commit
  the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* None open. (The pad, answered after session 10: a command-line
  schedule now, a burst of regular presses and releases rather than a
  held button; the window and keyboard later, with the display.)

## Later, not next

* The projector's fill rule for stretched, turned and bent cels (Opera
  has three paths: a line, a scale, an arbitrary quad filled by scanlines),
  then the rest the cel engine stops on.
* The display: a window (SDL3) showing the fields, with the VDL's display
  control words; then running in real time (the guest clock held back to
  the host's).
* The sound: native mixers for `mixer8x2`, `sampler`, `varmono8` and
  `dcsqxdhalfmono` (SDX2, the movie's sound) fed by the values the runtime
  keeps; the attachments' DSP side and the samples' ends; the audio
  folio's cues (`SignalAtTime`, `SleepUntilTime`: `_MEDPlayer`).
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
