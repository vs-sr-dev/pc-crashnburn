# Next session: the game played in its window -- the screens after a placed race

Where things stand: the translator is whole (`09-recompiler.md`, 22 seeds:
code only data reaches), and on 3dokit's Portfolio runtime `launchme`
boots, plays its logo and intro movies, and with seven presses of A goes
through Select Game, Select Character, Select Circuit, the circuit
champion's movie and the pre-race screen into the **race**, whose start
matches the user's Phoenix screenshots field for field once the grid is
the same (`08-oracle.md`). With A held it drives three laps -- along the
walls, through the water, the sand and the tunnel -- to the line in 6th
place, shows the **Rankout** screen (3 continues, CONTINUE and QUIT), runs
the race again on CONTINUE, and on QUIT unloads its sound and **ends**,
returning 1 to the OS after 935,186 calls. Session 13
(`03-executables.md`, "The race beside the real game, driven to its end")
added DeleteItem of a task, `UnloadInsTemplate` and a template's deletion,
`SetFunction` refused, `pfboot --pad ...+H` (a held press) and
`--frames-at`; after the wrap-up, at the user's choice, `pfboot --window`:
the display in an SDL3 window in real time, the keyboard and a gamepad as
the pad, `--record FILE` writing the presses as `--pad` options
(`tools/play.cmd`).

```sh
python -m 3dokit.recomp --out build/recomp --optest \
  "launchme=build/disc/launchme+154b4,158fc,19530,19540,195bc,195dc,250f8,25abc,26780,26fec,27908,27cec,2f314,449a8,44fb0,44fcc,45058,450c8,45138,451fc,45564,45648"
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
P="--pad a@1300x1 --pad a@4600x1 --pad a@4900x1 --pad a@6000x1 --pad a@6356x1 --pad a@7300x1 --pad a@7500x1"
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 100000 $P --frames DIR   # the race's start, Phoenix's grid
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 1300000 $P --pad a@7700+40000 \
  --frames DIR --frames-at 8000-60000/50        # three laps, Rankout, the race again (~2.5 min)
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 1100000 $P --pad a@7700+32500 \
  --pad down@40500x1 --pad a@40600x1            # ... QUIT: the program ends
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 [--trace 2] [--snap N DIR]
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
```

Run `python -m 3dokit.recomp` from `D:\Homebrew6` (the kit) while the kit
has uncommitted work. **Always give `--max-calls`**: the game waits for
ever on every screen. In the race `--frames` writes about 230 KB a field:
use `--frames-at` for anything long. Fields: dialog 1197, Select Game 4478,
Select Character 4642, Select Circuit 6187, the champion about 6356, the
pre-race screen about 7310, the race 7543, the start given about 7720, the
line about 40,300, Rankout 40,390.

## The work, in order

1. **What the user found in the window**: how its speed compares with
   Phoenix (the guest's 1 us a safe point sets how much a field holds;
   the window only holds the guest back), and the next stops the user's
   play reaches -- a placed race (`DoWinPlaceShow`, the purse,
   `DoBlackMarketScreen`, `DoEnhancementScreen`, the next track),
   Tournament, Options. A play that stops can be run again from
   `build/play-pad.txt` (`pfboot ... $(cat build/play-pad.txt)`), traced.
   Not modelled yet in the window: the display control words
   (interpolation), sound.
   **The guest's speed**: the user found the window smoother than Phoenix,
   the movies above all. Measured here: the intro movie shows 17.5
   distinct frames a second (350 in fields 2000-3199), the race 30 (one
   every two fields, the game's own cap: it never misses one). A safe point
   is worth 1 us (`pf_time.cpp`, an estimate); if the ARM60 here is faster
   than the console's, the game draws more than it would. To tell: the
   intro movie's length on Phoenix (here about 53 s, field 1306 to 4478)
   and its frames a second there; then `g_pf_safe_point_ns` calibrated.
2. **The kernel's messages on the 1993 code** (carried over): a `pfcheck`
   replay of `SendMsg`, `ReplyMsg`, `GetMsg` and `CreateSizedItem` of a port
   and a message on os_code (0x184d0, 0x186b8, 0x18bd4, 0x18418, 0x1898c),
   with `CheckItem`/`LookupItem` stood in for, the interrupt switches
   (0x106fc, 0x10720), `SendSignal` (0x19d40) traced; the game's calls 230
   to 239 and 402. A kit Python change: the battery.
3. Then the sound, Tournament, the Options screen.

## Keep in mind

* **The grid** is `rand`, advanced once a field by `GlueShell` while a menu
  waits: any change to the presses before the circuit is taken (6356)
  changes the grid -- 6300 gives the front row, 6356 Phoenix's back row.
  `RandomlySeedCars` (0x2374), `StartCars` (0x15178).
* **The pad in the race**: `TopOfFrame` reads it every field
  (`CNBReadJoystick`, 0x21b8); left and right steer, the control
  configuration's first mask accelerates (A in configuration 0; the table
  at 0x61f1c: A, C, L, R, B). The other four (C, L, R, B -- brake, weapons?)
  not yet read.
* **`--pad BUTTONS@FIELD[xN][/E][+H]`**: +H holds each press H fields (one
  press when no xN); E must exceed H. `--frames-at FIRST[-LAST][/EVERY]`.
* **A task's deletion** (`pf_task.cpp`): no resource table is kept -- the
  items the task owns, last made first, then those it opened; a task
  deleting itself stops (not yet); a thread whose function returns is
  marked gone but its items are not deleted (the kernel's 0x168fc would
  DeleteItem it). The dead task's host thread waits for ever.
* **The projector** (`3dokit/runtime/pf_cel.cpp`, `fill_quad`): WO
  94/10644's Regis unit -- corners cut to the integer below, rows from the
  polygon's top to (not including) its bottom, each from the left edge up
  to (not including) the right; ACW for rows whose left edge runs up, ACCW
  down. The patent's state tables are not in its text (`patent/wo644.txt`
  in session 12's scratchpad). Stops: `MARIA`, `TWD`, `SKIPX`, PIXC MS
  10/11, `LITERAL`, PRE0's BGND without the CCB's, an `LRFORM` cel not of
  16 bits, POVER 01, B15POS 10, USEAV's divider 3 or AV as source and
  control, PXOR with USEAV's subtraction, a read width unlike the write
  width.
* **Operamath** (`pf_math.cpp`): `MulManyVec3Mat33_F16` as MADAM's matrix
  engine computes it. **Cues** (`pf_audio.cpp`): the folio's timer list.
  **The OS's memory** (`pf_os.cpp`): a deleted item's node and name used
  again.
* **Seeds**: a run that stops with "a call to an address that is no
  function's entry" wants one more; `litcode.py` and `reloccode.py` in
  session 12's scratchpad scan for candidates (`09-recompiler.md`).
* **Audio**: nothing plays; a one-shot sample never ends.
* The rest as before: the event broker at its message boundary
  (`pf_event.cpp`), messages (`pf_msg.cpp`), files (`pf_file.cpp`:
  `{a|b}`, `FILECMD_GETPATH`, reads past a file's last block, `WaitIO` on a
  reply port and `GetDirectory` still stop), items never renumbered, the
  guest clock (`pf_time.cpp`), tasks on host threads one at a time,
  `--lenient` a preview only.
* The oracle is Phoenix (`08-oracle.md`), pictures and sound only; the
  user can also look at a field and say whether it is the real game's.
* Every 3dokit change: the battery when the kit's Python changes (give
  its script absolute output directories); the self-test (`selftest
  build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs, the sixteen Graphics snapshots); the
  three traces (`launchme` to its 234th call, Immercenary's `p`,
  OMF2097's `LaunchMe`) against session 12's (`tr12b` in its scratchpad,
  still the same); the 2,687 fields to Select Circuit (`--max-calls
  1300000`, the first six presses with 6300) against the last commit's
  build, byte for byte (build the old kit via `git stash` into a separate
  cmake directory). Scripts: session 11's `pfcheck.sh`, `traces.sh` (the
  self-test without its vectors: run that by hand) in
  `fb2fbdd2-.../scratchpad`; session 10's `cnb.dis`, `af.dis`,
  `graphix.dis` in `cfbf8bbb-.../scratchpad`; `battery.sh`, OMF2097's ISO
  and `rop-build` in `9e8e479d-.../scratchpad`; session 11's `kdis.py` and
  `os_code.bin`; session 12's `af.bin`, `om.bin`, the patent's text;
  session 13's `pair.py`, `zoom.py`, `sheet.py`, `grid.py` (the grid and
  `rand`'s state from a snapshot), `cars2.py`, `randsim.py`, `callers.py`
  in `d0e429b5-.../scratchpad`. Commit in the kit, `git pull --ff-only` in
  the submodule, commit the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc -- doc edits too.

## Questions for the user

* Next: placing in a race by a scheduled pad, or the window with the
  keyboard so that you drive?

(The Rankout screen: the user confirmed it is the real game's; the chosen
option flickers by design, CONTINUE by default.)

## Later, not next

* The sound: native mixers for `mixer8x2`, `sampler`, `varmono8`,
  `dcsqxdhalfmono` fed by the values the runtime keeps; the samples' ends.
* The event broker's other requests, other pods, `ControlPortChange`.
* Immercenary's `p`: `GetDirectory` next.
* The File folio's other calls; a CD's reading time.
* The kernel's quantum; item numbers reused as the kernel does; a thread
  that returns deleted as the kernel does (0x168fc).
* The timer's microseconds and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded (three
  laps take about 2.5 minutes without frames).
* A snapshot of the whole machine to start a run from.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` and `os_code`/`misc_code`; `portfolio --sites` on a
  decompressed image.
* The kernel's own lists (`kb_Devices` and the rest) not filled.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs.
