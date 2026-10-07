# Next session: the race -- looked at beside the real game, then driven

Where things stand: the translator is whole (`09-recompiler.md`, now with
22 seeds: code only data reaches), and on 3dokit's Portfolio runtime
`launchme` boots, plays its logo and intro movies, and with seven presses
of A goes through Select Game, Select Character, Select Circuit, the
circuit champion's movie and the pre-race screen into the **race**, which
it runs without stopping (over 260,000 fields tried): the road and the
desert textured, the sky, the HUD, the opponents going round on the
minimap -- and the player's car standing at the start, since nothing
presses the accelerator. Session 12 (`03-executables.md`, "Through the
screens to the race") added the projector for stretched, turned and bent
cels as 3DO's patent describes it, `USEAV` and `PXOR`, the audio folio's
cues and `ReleaseInstrument`, Operamath's `MulManyVec3Mat33_F16`, the clip
calls, and the OS's memory given back when an item is deleted.

```sh
python -m 3dokit.recomp --out build/recomp --optest \
  "launchme=build/disc/launchme+154b4,158fc,19530,19540,195bc,195dc,250f8,25abc,26780,26fec,27908,27cec,2f314,449a8,44fb0,44fcc,45058,450c8,45138,451fc,45564,45648"
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
P="--pad a@1300x1 --pad a@4600x1 --pad a@4900x1 --pad a@6000x1 --pad a@6300x1 --pad a@7300x1 --pad a@7500x1"
build/recomp-build/pfboot build/disc/launchme --trace 0 --max-calls 400000 $P --frames DIR   # to the race, ~10 s
build/recomp-build/pfboot build/disc/launchme --max-calls 34100 [--trace 2] [--snap N DIR]
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
```

Run `python -m 3dokit.recomp` from `D:\Homebrew6` (the kit) while the kit
has uncommitted work: run from the port it writes the submodule's runtime
into the CMakeLists. **Always give `--max-calls`**: the game waits for
ever on every screen, and in the race runs for ever. `--frames` writes a
picture for each changed field -- in the race nearly every field, 230 KB
each: a long race run wrote 25 GB; keep race runs short. The race's first
frames are at field 7543; the stages' fields: dialog 1197, Select Game
4478, Select Character 4642, Select Circuit 6187, the champion about
6356, the pre-race screen about 7310.

## The work, in order

1. **The race beside the real game**: a Phoenix screenshot of the race's
   start (the user's; Phoenix's shots sit at about 3.000 x 2.876 of
   ours), and the user's eye on the contact sheets, for the projector's
   rule above all (the patent's; Opera's paints one pixel more at each
   row's right). The first race frame is kept in session 12's scratchpad
   (`keep/vbl007547.ppm`).
2. **Driving**: `--pad` presses and releases (each held 6 fields); the
   race needs a button held -- a hold form for `--pad` (the user chose
   presses for session 11; ask before changing its meaning), and which
   button accelerates (the game's `GetJoystick` callers, `DrawHUD` and
   the car code, `03-executables.md`). Then lap after lap, to the race's
   end and what follows -- the next stops.
3. **The kernel's messages on the 1993 code** (carried over from session
   12): a `pfcheck` replay of `SendMsg`, `ReplyMsg`, `GetMsg` and
   `CreateSizedItem` of a port and a message on os_code (0x184d0, 0x186b8,
   0x18bd4, 0x18418, 0x1898c), with `CheckItem`/`LookupItem` stood in for,
   the interrupt switches (0x106fc, 0x10720), `SendSignal` (0x19d40)
   traced; the game's calls 230 to 239 and 402. A kit Python change: the
   battery.
4. Then, with the user: the display (an SDL3 window, the keyboard as the
   pad, real time) or the sound -- the game can now be played into a race.

## Keep in mind

* **The projector** (`3dokit/runtime/pf_cel.cpp`, `fill_quad`): WO
  94/10644's Regis unit -- corners from the corner engine (16.16 stepped
  by HDX >> 4; HDX stepped by HDDX at 20 bits), cut to the integer below;
  rows from the polygon's top to (not including) its bottom, each from the
  left edge up to (not including) the right, an edge's x from its upper end
  with the quotient cut toward 0; ACW for rows whose left edge runs up,
  ACCW down. The patent's state tables are not in its text
  (`patent/wo644.txt` in session 12's scratchpad, with the Munkee table at
  line 2248). After a cel HDX/HDY stay as HDDX/HDDY left them. Stops:
  `MARIA`, `TWD`, `SKIPX`, PIXC MS 10/11, `LITERAL`, PRE0's BGND without
  the CCB's, an `LRFORM` cel not of 16 bits, POVER 01, B15POS 10, USEAV's
  divider 3 or AV as source and control, PXOR with USEAV's subtraction, a
  read width unlike the write width.
* **The pixel processor's USEAV and PXOR** are Opera's order (secondary
  shifted by AV 4-3, complemented plus one to subtract, sign-extended,
  halved by 2D, clamped unless AV bit 2); Opera's 8-bit sum is not copied.
* **Operamath** (`pf_math.cpp`): `MulManyVec3Mat33_F16` as the Green
  MADAM's matrix engine computes it (Opera's 64-bit sum >> 16); the
  folio's software routines (a wirewrap's) truncate each product instead.
  Only that call is made.
* **Cues** (`pf_audio.cpp`): the folio's timer list in its node (+0xb0,
  the wake-up +0xa0/+0xac) run at the clock's tick, as the daemon would.
* **The OS's memory** (`pf_os.cpp`): a deleted item's node and name are
  used again for the next allocation of their size, most recent first.
* **Seeds**: a run that stops with "a call to an address that is no
  function's entry" wants one more; `litcode.py` and `reloccode.py` in
  session 12's scratchpad scan for candidates (`09-recompiler.md`).
* **Audio**: nothing plays; a one-shot sample never ends -- when the game
  asks whether a sound has finished, the sample's end (the FIFO's
  interrupt, 0x6578) needs a time.
* The rest as before: the event broker at its message boundary
  (`pf_event.cpp`), `pfboot --pad BUTTONS@FIELD[xN][/E]`, messages
  (`pf_msg.cpp`), files (`pf_file.cpp`: `{a|b}`, `FILECMD_GETPATH`, reads
  past a file's last block, `WaitIO` on a reply port and `GetDirectory`
  still stop), items never renumbered, the guest clock (`pf_time.cpp`),
  tasks on host threads one at a time, `--lenient` a preview only, the
  OS's structures as the SDK headers have them checked against the 1993
  code.
* The oracle is Phoenix (`08-oracle.md`), pictures and sound only; the
  user can also look at a field and say whether it is the real game's.
* Every 3dokit change: the battery when the kit's Python changes (give
  its script absolute output directories); the self-test (`selftest
  build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt`);
  `pfcheck` (the six memory runs, the sixteen Graphics snapshots, calls 0,
  8, 9, 11, 12, 14, 15, 17 to 20, 626, 627, 645, 2101, 2104); the three
  traces (`launchme` to its 234th call, Immercenary's `p`, OMF2097's
  `LaunchMe`); and now the 2,687 fields to Select Circuit
  (`--max-calls 1300000`, six presses) against the last commit's build,
  byte for byte. Scripts: session 11's `pfcheck.sh`, `traces.sh` (it calls
  the self-test without its vectors: run that by hand), `sheet2.py`,
  `kdis.py` in `fb2fbdd2-.../scratchpad`; session 10's `ccbwalk.py`, the
  guide's chapters as text, `graphix.dis`, `af.dis`, `cnb.dis` in
  `cfbf8bbb-.../scratchpad`; `battery.sh`, OMF2097's ISO and `rop-build`
  (run `cmake` again when the runtime gains a file) in
  `9e8e479d-.../scratchpad`; session 12's `om.bin` (OPERAMATH), `af.bin`,
  `hw.dis` (0x44000 on), the patent's text, `litcode.py`, `reloccode.py`,
  `tables.py` in `3997990a-.../scratchpad`. Commit in the kit, `git pull
  --ff-only` in the submodule, commit the port, record in `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc -- doc edits too (session 12 slipped again:
  an assert caught it).

## Questions for the user

* Can you take a Phoenix screenshot at the race's start (Rally,
  Hammerhead, Crash Course track 1, just after the pre-race screen's
  RACE), to set beside `keep/vbl007547.ppm`?
* For driving: a held button for `--pad` (say `a@7600+600` for 600 fields
  held), or a new flag?

## Later, not next

* The display: a window (SDL3) with the VDL's display control words, the
  keyboard as the pad, real time (the guest clock held to the host's).
* The sound: native mixers for `mixer8x2`, `sampler`, `varmono8`,
  `dcsqxdhalfmono` fed by the values the runtime keeps; the samples' ends.
* The event broker's other requests, other pods, `ControlPortChange`.
* Immercenary's `p`: `GetDirectory` next.
* The File folio's other calls; a CD's reading time.
* The kernel's quantum; item numbers reused as the kernel does.
* The timer's microseconds and `CMD_STATUS`; SPORT's own range checks.
* The emitter's speed: flags only where read, literal pools folded (the
  race ran at about 10,000 fields a minute with `--frames`, nearly three
  times real time).
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` and `os_code`/`misc_code`; `portfolio --sites` on a
  decompressed image.
* The kernel's own lists (`kb_Devices` and the rest) not filled.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs.
