# Next session: the game is done; a second title

Where things stand: the translator is whole (`09-recompiler.md`: 22 seeds
for `launchme`, 3 for `/Orion`), and on 3dokit's Portfolio runtime the
**disc starts as the console starts it** (`pfboot build/disc --boot`, the
shell carrying out its scripts): `/ex` (= `launchme`, the game) and
`/Orion` (the Total Eclipse preview, a real-time 3D flight) in turn, for
ever. The game plays its logo and intro movies, its menus, and races --
the start matching the user's Phoenix screenshots once the grid is the
same, three laps driven, the pits (RELOAD, REPAIR), the Rankout screen;
the pause menu's QUIT ends the program and the preview follows, then the
game again from its logo, as on the user's FZ-10 (`08-oracle.md`).
`tools/play.cmd` plays the disc in an SDL3 window in real time, the
keyboard or a gamepad as the pad, the presses recorded. **The user's
verdict: at par with Phoenix** -- smoother where the console struggles (no
time is counted for the cel engine: left so, by the user's choice) -- and
since session 15 **with its sound, which the user heard right**: the
menus, the music, the effects, the movies; a race ends and the second
circuit loads. By the user's rule the game is done: **it works until shown
otherwise** (a stop in the user's play is replayed from its record and
fixed).

Session 15 (`00-sessions.md`, `03-executables.md`'s last section) gave the
kit the DSP (`3dokit/runtime/pf_dsp.cpp`): the instruments the two
programs load transliterated from their DSP code, the DMA as AUDIOFOLIO
programs it, the sound made in the guest's time, to `--wav` and the
window. Session 14 made the guest's clock count the ARM60's clocks, read
the movies' pace in their file, and gave the kit the shell.

```sh
python -m 3dokit.recomp --out build/recomp --optest \
  "launchme=build/disc/launchme+154b4,158fc,19530,19540,195bc,195dc,250f8,25abc,26780,26fec,27908,27cec,2f314,449a8,44fb0,44fcc,45058,450c8,45138,451fc,45564,45648" \
  "Orion=build/disc/Orion+2cd8,11138,1bef0"
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc --boot --trace 0 --max-calls N [--pad ...] [--window]   # the whole disc
build/recomp-build/pfboot build/disc --boot --trace 0 --max-calls 2000000 $(cat build/play-pad-pause.txt)  # QUIT, Orion, the game again
build/recomp-build/pfboot build/disc/Orion --trace 0 --max-calls 300000   # the preview alone: exit(0) at 216,101
P="--pad a@1300x1 --pad a@4600x1 --pad a@4900x1 --pad a@6000x1 --pad a@6405x1 --pad a@7349x1 --pad a@7549x1"
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 100000 $P --frames DIR   # the race's start, Phoenix's grid
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 1300000 $P --pad a@7749+40000 \
  --frames DIR --frames-at 8000-60000/50        # three laps, Rankout, the race again (~3 min)
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 1100000 $P --pad a@7749+32711 \
  --pad down@40670x1 --pad a@40770x1            # ... Rankout's QUIT: the program ends
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 [--trace 2] [--snap N DIR]
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
```

Run `python -m 3dokit.recomp` from `D:\Homebrew6` (the kit) while the kit
has uncommitted work. **Always give `--max-calls`**: the game waits for
ever on every screen, and through `--boot` the disc never ends. In the
race `--frames` writes about 230 KB a field: use `--frames-at` for anything
long. **Never `--trace 1` a long run into a file** (a replay to the pits
wrote 6.8 GB): pipe it through `grep` or `tail`. Fields (the game alone):
dialog 1210, Select Game 4495, Select Character 4645, Select Circuit 6187,
the champion about 6415, the pre-race screen about 7357, the race about
7602, the line about 40,450, Rankout 40,560.

## The work, in order

The user's plan: the game counts as done ("it works until shown
otherwise"); the work moves to **a second title** to draw 3dokit out
further -- **Total Eclipse** among the titles to come (its preview,
`/Orion`, already runs here, with its sound). Which title, and whether in
this repository's sibling or a new port, is the user's to say.

1. **The second title** (a new port on 3dokit, as this one took the kit
   from Immercenary): its disc read (`disc`, `aif`, `cel`, `audio`, `dsp
   --used`), its programs recompiled, its run on the runtime to its first
   stop, and from there as here. What it will likely ask of the kit: DSP
   instruments no program loaded yet (each a transliteration of its code,
   `pf_dsp.cpp`'s `kModels`; an unknown one plays silent and says so
   once), envelopes, other folio calls; the event broker's other devices.
2. **This game, when the user's play shows something**: replay the
   record (`pfboot build/disc --boot $(cat build/play-pad.txt)`; kept:
   `build/play-pad-pit.txt` to the pits, `play-pad-lap2.txt` lap 2,
   `play-pad-pause.txt` the pause's QUIT) and fix the stop. Not reached
   yet as far as the user has said: Tournament, Options, the black market
   and enhancement screens after a placed race. Not modelled in the
   window: the display control words (interpolation).
3. **The kernel's messages on the 1993 code** (carried over): a `pfcheck`
   replay of `SendMsg`, `ReplyMsg`, `GetMsg` and `CreateSizedItem` of a port
   and a message on os_code (0x184d0, 0x186b8, 0x18bd4, 0x18418, 0x1898c).

## Keep in mind

* **Before "fixing" a glitch**, read what the disc's code does there and
  ask the user to look on Phoenix and the console: the radar's leak is the
  original's (GRAPHIX's `SetClipOrigin`, `03-executables.md`). But a
  recompilation keeps what the code does, not the hardware's limits: the
  console's dropped frames are not to be reproduced (`08-oracle.md`).
* **The shell** (`pf_file.cpp`, `pf_shell_boot`): each program boots a fresh
  OS; the guest's clock, GRAPHIX's field count and the timer's go on, so a
  `--pad` field is the whole run's. On the console the OS stays loaded
  (item numbers, its memory): not modelled. `bg`, `bgkill`, `killkprintf`,
  `minmem` passed over; the OS's programs under /System are the runtime's.
* **The grid** is `rand`, advanced once a field by `GlueShell` while a menu
  waits and once a loop on the logo movie (the CPU's speed moves it too):
  6405 gives `Random(12)` = 3 (2,549 calls), Phoenix's back row; the circuit
  screen reads the pad every 7 fields. `gridpick.py` (session 14).
* **The guest's clock** (`pf_time.cpp`, `recomp/emit.py`'s `clocks`): the
  ARM6 datasheet's cycles, an N cycle two clocks, a failed condition one,
  a multiply's from rs, paid a block at a time; 80 ns a clock. Not counted:
  the OS's work, the cel engine's and DMA's share of the bus, the CD.
* **Hand-written code** (`recomp/discover.py`): `add/sub lr, pc, #k` before
  a pc write is a call; a word lr is set to that the descent reaches in
  the function is a local subroutine's return (`local_returns`; not
  followed from lr alone: the 3D code also points lr at tables).
* **The pad in the race**: `TopOfFrame` reads it every field
  (`CNBReadJoystick`, 0x21b8); left and right steer, the control
  configuration's first mask accelerates (A in configuration 0; the table
  at 0x61f1c: A, C, L, R, B).
* **`--pad BUTTONS@FIELD[xN][/E][+H]`**: +H holds each press H fields (one
  press when no xN); E must exceed H. `--frames-at FIRST[-LAST][/EVERY]`.
* **A task's deletion** (`pf_task.cpp`): no resource table is kept; a dead
  task's host thread waits for ever (so do a finished program's threads).
* **The cel engine** (`3dokit/runtime/pf_cel.cpp`): the projector as WO
  94/10644's Regis unit; PIXC MS 10/11 as Opera reads them (the guide says
  the colour's bits the other way round); TWD looks at the first pixel's
  turn. Stops: `MARIA`, `SKIPX`, `LITERAL`, PRE0's BGND without the CCB's,
  an `LRFORM` cel not of 16 bits, POVER 01, B15POS 10, USEAV's divider 3 or
  AV as source and control, PXOR with USEAV's subtraction, a read width
  unlike the write width.
* **`LoadSample`** (`pf_audio.cpp`): the folio's IFF reader on a File folio
  stream; a chunk other than SSND above 500 bytes, a FORM or XREF inside,
  stop (the folio would read a stale buffer, or nest).
* **The DSP** (`pf_dsp.cpp`): an instrument is its code transliterated,
  matched by the code's checksum (`kModels`); `python -m 3dokit.dsp FILE
  --dis` reads a new one. The sound is made up to the guest's present at
  each folio call that changes the DSP and at each audio tick; it never
  changes what the program sees but for the folio's daemon at an armed
  chunk's end. A stopped instrument's `Output` keeps its last value (the
  folio's own way). Not modelled: envelopes, the FIFO's buffering, cues on
  attachments, output FIFOs (delay lines). Test runs with a window: set
  `SDL_AUDIO_DRIVER=dummy` as well as `SDL_VIDEO_DRIVER=dummy`.
* **Seeds**: a run that stops with "a call to an address that is no
  function's entry" wants one more; `litcode.py` and `reloccode.py` in
  session 12's scratchpad scan for candidates (drop those whose first word
  is no instruction: variables).
* The rest as before: the event broker at its message boundary, messages,
  files (`{a|b}`, `FILECMD_GETPATH`, `WaitIO` on a reply port and
  `GetDirectory` still stop), tasks on host threads one at a time,
  `--lenient` a preview only.
* Every 3dokit change: the battery when the kit's Python changes (give its
  script absolute output directories; c6a174b's is ac527c2's byte for
  byte); the self-test (`selftest
  build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs, the sixteen Graphics snapshots -- the late
  ones 1092 1093 1111 2101 2102 since the drive's reading time, the same
  calls that were 624 625 643: PC-Immercenary session 24's `pfcheck3.sh`); the three traces
  against `tr14`; the 1,131 frames of `--max-calls 100000` (to field 3216)
  and the 2,974 of fields 8000-14,000 (presses with 6405, A from 7749)
  against the last commit's build, byte for byte (session 15's
  `frames.sh` takes the two builds; the baseline is 3dokit 5ff9786's, the
  first with the drive's time, and the presses land at other moments
  than they were written for). A change to the emitter or discovery
  means regenerating Immercenary's and OMF2097's C++ too (session 14's
  `rop`, `rop-build`). Scripts in session 14's scratchpad
  (`bc5937c1-.../scratchpad`): `traces.sh` (takes two pfboot builds),
  `pfcheck.sh`, `instrument.py`, `cycles.py`, `byfunc.py`, `split.py`,
  `same.py`, `align.py`, `seqcmp.py`, `cropcmp.py`, `gaps.py`, `gdis.py`
  (GRAPHIX disassembled at a slot or address), `gridpick.py`,
  `sdiv_ref.py` and `sdiv_test.cpp`; `battery.sh` in `0fb6cb89-...`;
  session 10's `cnb.dis`, `af.dis`, `graphix.dis` in `cfbf8bbb-...`;
  OMF2097's ISO in `9e8e479d-...`; session 12's `af.bin`, `om.bin`,
  `litcode.py`, `reloccode.py`, the patent's text in `3997990a-...`;
  session 13's `sheet.py`, `pair.py`, `zoom.py`, `grid.py`, `randsim.py`
  in `d0e429b5-...`; session 15's `frames.sh`, `wavstat.py` (a WAV's
  loudness over time), `sdx2cmp.py`, `ringcmp.py`, `wrapcmp.py` in
  `3a174178-...`. Commit in the kit, `git pull --ff-only` in the
  submodule, commit the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc -- and any source edit through Edit.

## Questions for the user

* Which second title, and where: a new port repository on 3dokit (as this
  one), Total Eclipse or another?

## Later, not next

* The event broker's other requests, other pods, `ControlPortChange`.
* Immercenary's `p`: `GetDirectory` next.
* The File folio's other calls; a CD's reading time.
* A persistent OS from one program to the next (the shell's runs).
* The kernel's quantum; item numbers reused as the kernel does; a thread
  that returns deleted as the kernel does (0x168fc).
* The timer's microseconds and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded.
* A snapshot of the whole machine to start a run from.
* Ghidra's function list against discovery's (`--against`).
* The kernel's own lists (`kb_Devices` and the rest) not filled.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs.
