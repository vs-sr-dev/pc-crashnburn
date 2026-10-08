# Sessions

## Session 1 (2026-10-06) — the kit split out, the code surveyed, the plan

* **3dokit is a repository of its own** (`10-3dokit.md`): split out of
  pc-immercenary with its history and taken here as a submodule. Its
  third disc: `disc`, `cel` (60 of 60 pictures), `audio` (17 of 17 AIFF)
  read it unchanged; `aif` learnt where the relocation stub is, `dsp` the
  instrument format's version 1, `arm` the compiler's embedded names.
* **The disc** is the one the documentation pipeline measured
  ([3do-crashnburn-doc](https://github.com/vs-sr-dev/3do-crashnburn-doc)):
  USA/Korea, one track, 451 files. The kit reads it the same.
* **The code** (`03-executables.md`): `/launchme`, Norcroft ARM C, 584
  functions, the game's 292 named by the compiler. Indirect jumps all
  bounded: 116 folio vectors, 17 switches, 15 calls through function
  pointers with 45 targets found by the relocations. No hardware access.
  The OS surface: 35 SWI entry points, 75 attributed folio vector slots
  plus Graphics' 38; four DSP instruments.
* **The route** (`06-attack-plan.md`): static recompilation with HLE at
  the Portfolio boundary, the translator and runtime built as 3dokit's
  layers 4 and 5. The oracle is Opera (libretro) with `panafz10.bin`,
  both already in `F:\RetroArch 2`.

## Session 2 (2026-10-06, the same day) — the OS named, the oracle, discovery

* **The OS surface, named** (`03-executables.md`): the 3DO SDK's headers
  (1.2, 1.3, 2.5) and the 3do-devkit's libraries give every SWI and folio
  slot its name (`3dokit.sdk`, `3dokit.aof`). What the game's code really
  reaches is 33 SWIs and 41 slots: Graphics 14 (`DrawCels`, `MapCel`,
  screen groups, `DisplayScreen`...), Kernel 11, audio 12, File 4.
* **The startup**: KernelBase in r7, Kernel slot -120 before `main`, the
  stack check's slot -124.
* **The oracle** (`08-oracle.md`): Opera loops in the Preview and never
  reaches the game, whatever the BIOS or timing hack; the user's own
  pressing, read from their drive, is the image to the sector; **Phoenix
  2.8 runs it**: the logo, the choice between the game and the Preview,
  the intro movie, the menu (Rally, Tournament, Options).
* **The translator begins** (`09-recompiler.md`): `3dokit.arm60`, the
  instruction set decoded exactly, and `3dokit.recomp.discover`: 553
  functions, 16 switches, 8 indirect transfers outside the OS's, 17 dead
  functions, code past `code_end` in the read-write area.

## Session 3 (2026-10-06, the same day) — the translator whole, the OS begun

* **The interpreter** (`3dokit.armemu`): ARMv3 in user mode with the
  ARM60's own rules (the unaligned `ldr`'s rotation, `pc` + 12 under a
  register shift and when stored, `ldm`/`stm` with the base in the list),
  8 known-answer tests, and 27,819 random instructions that agree with
  unicorn's ARM926. `Arctan` and `Distance` run in it as the game's code.
* **The emitter and the self-test** (`09-recompiler.md`): `launchme`
  recompiles whole, 553 functions and 43,805 instructions with nothing
  refused, and builds in seconds. The interpreter records and the C++
  replays: an instruction test of 891 functions (10,580 vectors) and the
  138 game functions that run without the OS (2,083 vectors), 0 failures;
  two faults injected by hand are caught. Eight programs of the kit's
  other two discs recompile and replay too (1,016 functions, 0 failures).
* **The eight indirect transfers**, read to the end: two pointer calls, the
  drivers' table as a tail jump, the 3D routine's handler word, and four
  `ldr pc` that are **returns** through an `lr` the routine parked in a word
  of its own -- session 2 had read them as tables after the call
  (`03-executables.md` corrected). Discovery now finds them.
* **Phase 4 begins** (`3dokit/runtime/pf*`, `pfboot`): the program boots
  on a Portfolio frame, the folio tables hold traps, every SWI and slot is
  traced by its SDK name. `launchme` calls the startup's Kernel slot -120,
  prints `...cnb...` with `kprintf`; with items and `ChangeDirectory` it
  then finds and opens the Graphics folio by name, and stops at `FindMH`,
  the memory lists'. Phoenix exposes no debug output (the user's look): it
  is the oracle for pictures and sound only.

## Session 4 (2026-10-06, the same day) — memory, read in the 1993 kernel

* **Why memory first**: the game reaches `FindMH` through lib3DO's
  `GetMemType` of `GrafBase->gf_ZeroPage`, to put its screens in the zero
  page's VRAM bank, and it walks the memory lists itself every frame
  (`WriteMemoryUsageToRam`): the structures have to be `mem.h`'s, in guest
  memory (`03-executables.md`, "Memory").
* **The OS on the disc, read**: `3dokit.aif --decompress` runs a compressed
  image's own decompressor in the interpreter, and the 1993 kernel
  (`os_code` v0.16) and Graphics folio (`GRAPHIX`, 16 August 1993) became
  readable. From them: the kernel's vector table and its backwards SWI
  table, slot -120 (the command line's parser), the MemHdrs and MemLists
  the kernel builds, its allocator, and what the Graphics folio puts in
  its node when it starts.
* **3dokit's memory** (`runtime/pf_mem.cpp`): the allocator as the kernel
  runs it, checked by **replaying** it on the kernel's own code
  (`pfboot --memtest`, `python -m 3dokit.pfcheck`): 24,000 calls, every
  result and every byte of guest memory the kernel's; two faults put in by
  hand are caught. The Graphics folio's node is filled as GRAPHIX fills it.
* **Where the run stops**: `FindMH` of the zero page answers the VRAM
  MemHdr, the game asks for two screens in that bank, and stops at
  `CreateScreenGroup`, whose user half and supervisor half (SWI 0x20032,
  0x27a0 in GRAPHIX) are the next session's.

## Session 5 (2026-10-06/07) — the screens, and the first device

* **The screens, read in GRAPHIX** (`03-executables.md`): the 1993 folio's
  own node sizes (its ScreenGroup and VDL are shorter than the headers'),
  its system VDLs, `CreateScreenGroup`'s user half and SWI 50 to the end
  of the type the game uses, `AddScreenGroup` and the averaging calls,
  and the kernel's `CheckItem` and its 1993 write check (slot -168).
  3dokit now makes all of them the same way.
* **A Graphics call is checked on GRAPHIX itself**: `pfboot --snap N DIR`
  writes the memory before and after the N-th OS call, and `pfcheck
  --graphix` replays it on the folio's own code, loaded at 0x700000 by its
  own relocations (`aif.relocated`), with the kernel's own allocator,
  `InitList`, `CheckItem` and write check. The folio's start of its VDLs
  and the game's ten Graphics calls agree byte for byte; the first run
  found a wrong constant in the runtime, and two faults put in by hand
  are caught.
* **Devices and IO, read in the kernel**: IOReqs, `SendIO` and
  `CompleteIO` as the 1993 kernel runs them, with the task's signals. The
  SPORT device is not on the disc (the console's ROM brings it; the ROM's
  own programs only open it), so the runtime's follows the SDK's
  documentation, its copies done at once rather than at the vertical
  blank. The game clears its two screens with it.
* **Where the run stops**: `Initing Sounds and Music`, the audio folio
  opened, and its first call, `LoadInsTemplate` of `mixer8x2.dsp`: the
  sound is next. Immercenary's `p` runs on to its 113th call.

## Session 6 (2026-10-07) — the sound's set-up, and the first thread

* **The audio folio, read** (`03-executables.md`): AUDIOFOLIO V20.19
  (5 September 1993) -- its tags, node database, 42 vectors, 32 SWIs run
  backwards, its item routines, and every call the game's `InitSound`
  makes: four templates loaded from the disc, the `mixer8x2` mixer, eight
  voices (`sampler` and `varmono8`) with their knobs and gains, each
  connected to the mixer, the mixer started, 59 empty samples. 3dokit now
  makes these items the same way, without the DSP: every value the folio
  would write to it is kept for a native mixer. A knob's calculation types
  went into `3dokit.dsp`.
* **The kernel's `vfprintf`** writes through the program's own `putc`, as
  the 1993 C library's printf core does: the runtime calls back into the
  recompiled code. OMF2097's `LaunchMe` now prints its banner and stops
  at its 36th call.
* **The first thread**: the game's "sound service", which waits for its
  signal at a priority above the game's and then drives the voices.
  CreateTask's thread, signals, `SetItemPri` and the kernel's switch read
  in os_code, and the runtime runs each task on a host thread of its own,
  one at a time; the program runs at the shell's spawn priority, 100. The
  1993 CreateTask's reschedule test is the wrong way round (a new
  higher-priority thread waits for the quantum tick).
* **Checks**: the battery's 51 outputs byte-identical across the kit's
  change; the self-test; `pfcheck`'s six memory runs and eleven Graphics
  replays clean from the new boot; Immercenary's `p` unchanged.
* **Where the run stops**: the game's 218th call, `OwnAudioClock`: the
  audio clock, then the File folio's streams (`CNB/Glue/Chars.bin`). Time
  is next.

## Session 7 (2026-10-07) — time, and the console ROM

* **Time** (`03-executables.md`, "Time"): what the game times -- its frame
  waits for the vertical blank (`WaitVBL` on the timer device), its sound
  runs on the audio clock at 128 Hz (`InitTimer`), its music sleeps on a
  cue -- and what the 1993 OS does: GRAPHIX's VBL FIRQ, the audio folio's
  clock (its DSP countdown, the daemon's 240 Hz, `OwnAudioClock` a
  semaphore lock, `SetAudioRate`'s rounding through Operamath's
  `DivUF16`, run on its own code), the kernel's semaphores, quick IO.
* **The decision of the session**: the runtime's clock is the guest's own,
  1 us per safe point of the recompiled code and a jump to the next event
  when every task waits, so every run gives the same trace on any host;
  events stand for the interrupts (the vertical blank, the audio tick) and
  a higher-priority task they make ready runs at once. A run in real time
  will hold the guest back to the host's clock, later.
* **The console ROM** (`03-executables.md`, "The console ROM"): the File
  folio, the timer and SPORT are not on the disc. With the user's go-ahead
  the FZ-1's ROM is read locally (never committed): `3dokit.rom` reads its
  Opera volume (4-byte blocks) and unpacks its fifteen programs, among them
  the Operator (3 August 1993) and the File folio. The runtime's SPORT and
  timer, written from the SDK in sessions 5 and 7, were checked against the
  Operator and corrected: a delay of 0 blanks waits for the next one,
  `DELAYUNTIL` subtracts the 1993 way round, a command done at once makes
  `SendIO` return 1.
* **Checks**: the battery's 51 outputs byte-identical; the self-test; the
  six memory runs and the eleven Graphics snapshots pass `pfcheck` from the
  new boot (three more items: the clock's two semaphores and the timer).
  OMF2097's `LaunchMe` unchanged; Immercenary's `p` now finds its timer and
  waits out 47 blanks, to its 351st call.
* **Where the run stops**: `launchme` clears its screens at the first two
  blanks, takes the audio clock, sets 128 Hz, and stops at its 234th call,
  the File folio's `OpenDiskStream` of `CNBSFX/gun.sfx`. Files are next,
  read in the ROM's File folio.

## Session 8 (2026-10-07) — the File folio, read in the ROM

* **The File folio, read** (`03-executables.md`, "The File folio, read in
  the ROM"): its 14 SWIs run backwards like the kernel's (SWI 0,
  `OpenDiskFile`, is 0x3388); the path walker (0x2614), with `$aliases`
  substituted and walked on, `^` the filesystem's root, names without case;
  an open file is a device of the folio's own driver, whose `CMD_STATUS` is
  answered at once and whose reads, whole blocks only, go to the CD's queue
  and come back later; the four stream functions are user-mode code over
  those calls.
* **Where `$exdir` comes from**: not the game, not the ROM. The disc's own
  shell (`System/Tasks/shell`) makes `alias boot /` followed by a name the
  kernel keeps (at KernelBase + 0x110: the boot volume's, it seems), goes there and runs `^/system/scripts/startopera` (`audio`,
  `drivers`, `c`, `s`, `app`), which runs `^/AppStartup`: `alias exdir
  $boot`. The runtime reads those scripts for their aliases.
* **The disc's fill**: past every file's end, to the end of its last block,
  the disc holds "iamaduck" over and over, by the byte's place in its
  block -- 414 of the 415 files here that end inside a block (not
  `rom_tags`) and 1,495 of 1,497 on OMF2097. The
  runtime's reads give the same bytes.
* **3dokit** does all of it the folio's way (`runtime/pf_file.cpp`), with
  the kernel's `DeleteItem` for IOReqs and devices: the streams step for
  step, their IOInfos and the file's status on the caller's stack where the
  folio's frames put them.
* **Checks**: the self-test; the six memory runs and eleven Graphics
  snapshots pass `pfcheck`; OMF2097 unchanged; Immercenary's `p` gets one
  call further (its timer's IOReq deleted). `gun.sfx` read through the
  stream is the disc's file byte for byte.
* **Where the run stops**: `launchme` loads all fourteen sound effects
  (open, seek to the end and back, read, close) and stops at its 240th
  call, the audio folio's `SetAudioItemInfo` on the first one's sample. In
  the `--lenient` preview it then reads `$exdir/CNB/Glue/Chars.bin` and
  `Plate.3do`, opens `$boot/bigfile` and reads it through eight IOReqs of
  its own, and up to its 1,200th call the only other calls missing are
  GRAPHIX's `SetScreenColor` and `DisplayScreen`.

## Session 9 (2026-10-07) — the samples, the screen, and the first movie

* **The sound effects' samples**: `SetAudioItemInfo` read in AUDIOFOLIO --
  a sample's tags stored as they come, frames and bytes kept in step,
  loops bounded, the base frequency from the folio's default tuning (440
  Hz at note 69) and Operamath's `MulUF16` (its code agrees on 3,004
  cases). The kernel check the folio makes on its pointers returns 0 or 1,
  which the folio tests as an Err: it never refuses. All fourteen samples
  are taken.
* **The screen**: GRAPHIX's `SetScreenColor(s)`, `ResetScreenColors` and
  `DisplayScreen`, and the blank's linking of the field's VDL; replayed on
  the folio with `pfcheck` (now sixteen Graphics snapshots, byte for byte).
  `pfboot --frames DIR` writes what the VDLs show at each blank that
  changes it. The game fades its screen in and out -- still black.
* **The movie's voice**: `DisconnectInstruments`, `DeleteItem` of knobs and
  instruments through the folio's `ir_Delete` (a new kernel hook), a sample
  made with tags, attachments (`AttachSample`, `DetachSample`) and
  `LinkAttachments`.
* **The first picture**: with those, `launchme` plays the Crystal Dynamics
  logo movie (`EXTRA.1`) to its end -- 20 seconds of guest time, its own
  code decoding into its two screens, 530 different fields written by
  `--frames`. Nothing is heard (no DSP).
* A stop inside an OS call now names the call's site: compiled code uses
  `lr` as a register too (the sound code counts with it).
* **Checks**: the self-test; six memory runs and sixteen Graphics snapshots;
  OMF2097 unchanged; Immercenary's `p` two calls further (to
  `UnloadSample`).
* **Where the run stops**: the 14,822nd call, `StopInstrument` on the
  movie's voice, once the logo has played.

## Session 10 (2026-10-07) — the movie's end, the cel engine, the choice dialog

* **The voice stopped**, read in AUDIOFOLIO: `StopInstrument`, the states
  the folio keeps (an instrument's, its DSP side's, each attachment's, the
  attachment each FIFO plays), `StartInstrument` starting only each FIFO's
  first attachment without `NOAUTOSTART`, and deletion of a playing
  attachment and of a sample. The game then takes the movie's sound down
  and puts `varmono8` back on voice 0.
* **The cel engine** (`3dokit/runtime/pf_cel.cpp`), behind GRAPHIX's
  `DrawCels` -- which only writes MADAM's registers and waits: written from
  the 3DO Graphics Programmer's Guide (chapters 3 and 5, in the
  3do-devkit's docs), with Opera's MADAM read where the guide is silent
  (the pixel processor drops each stage's fraction, 2D halves the sum; a
  packed row ends at its last word; the V and H bits; relative pointers as
  `MakeCCBRelative` makes them, which Opera agrees with). The projector
  draws only square cels for now; the rest stops the run.
* **The choice dialog**: CRASH'N BURN lit and PREVIEWS dimmed, from
  `IntroScreen.3DO`, drawn each frame; beside Phoenix's screenshot the
  buttons' faces agree within a level or two of 255
  (`08-oracle.md`).
* `pfboot --snap` now also works on a call not implemented yet.
* **Checks**: the three traces byte for byte, the self-test, six memory
  runs, sixteen Graphics snapshots.
* **Where the run stops**: it does not -- the dialog waits on the pad for
  ever. The game's input library found no event broker (`FindItem` of the
  MsgPort "eventbroker" at its 229th call) and its `GetControlPad` returns
  -1. Next: the kernel's messages and the broker.

## Session 11 (2026-10-07) — the pad: messages, the event broker, the menu

* **The kernel's messages**, read in os_code (`03-executables.md`): ports,
  messages, `SendMsg`, `ReplyMsg`, `GetMsg`, `GetThisMsg`, their deletion
  (`3dokit/runtime/pf_msg.cpp`).
* **The event broker**: the disc's `System/Tasks/eventbroker` (August
  1993) read; its Control Port driver is nowhere on the disc or in the
  ROM's Operator, so -- the user's choice -- the runtime does what the
  broker does at its message boundary (`pf_event.cpp`): the
  "eventbroker" port, `EB_Configure`, listeners and focus, an
  `EB_EventRecord` each field the pad changes.
* **A pad for `pfboot`**: `--pad BUTTONS@FIELD[xN][/E]`, presses each
  released after 6 fields.
* **Correction**: the game's input library asks to be an observer
  (`LC_Observer`), not a focus listener.
* **The game goes on**: with A at field 1300 the dialog takes CRASH'N
  BURN, the intro movie plays, and the Select Game menu appears at field
  4478 -- the real game's, the user confirms. A second A takes Rally: the
  Select Character screen.
* **Checks**: `LaunchMe` byte for byte; `launchme` and `p` differ as
  expected (the port's item; `p` now reaches `GetDirectory`); self-test, six
  memory runs, sixteen Graphics snapshots (five renumbered).
* **Where the run stops**: it does not; with two presses of A it reaches
  Select Character (field 4642) within 400,000 calls.

## Session 12 (2026-10-07) — through the screens into the race

* **The cel engine's next bits**: PRE0's BGND bit (the SDK's libraries set
  it with the CCB's; Opera never reads it) and `LRFORM` -- the Select
  Character portrait. Then the **projector** for stretched, turned and
  bent cels, from 3DO's patent WO 94/10644 (the Regis unit: corners cut to
  the integer below, rows filled up to but not including the right edge,
  the bottom row left out, ACW/ACCW from each row's left edge); on square
  cels it draws what the runtime drew before, pixel for pixel. `USEAV` and
  `PXOR` in the pixel processor as Opera combines them.
* **The audio folio's cues** (the music player's `SleepUntilTime`), read
  in AUDIOFOLIO: the folio's timer list, `SignalAtTime`, `GetCueSignal`,
  the clock's wake-up; and `ReleaseInstrument`.
* **Operamath**, read: `MulManyVec3Mat33_F16` runs on MADAM's matrix engine
  on retail consoles; the runtime computes as the engine does (Opera's
  arithmetic), not as the folio's software fall-back rounds.
* **GRAPHIX's clip calls**: `SetClipOrigin`, `SetClipWidth`,
  `SetClipHeight`.
* **The recompiler's seeds**: 22 entries only data reaches -- the objects'
  state-machine dispatchers and handlers, a callback, the models' entries
  into the hand-written renderer -- given on the command line
  (`09-recompiler.md`); a scan of relocated words and literals shows the
  rest of the candidates are data.
* **The OS's memory given back**: a deleted item's node and name are used
  again; without it the race filled the OS's memory at field 53,850.
* **Checks**: the three traces byte for byte, self-test 0 failures, six
  memory runs, sixteen Graphics snapshots; the 2,687 fields to Select
  Circuit byte for byte against the previous build.
* **Where the run stops**: it does not. With seven presses of A the game
  goes through Select Character, Select Circuit, the champion's movie and
  the pre-race screen into the race (field 7543), which runs past field
  260,000 -- the opponents racing, the player's car standing at the start.

## Session 13 (2026-10-07) — the race beside Phoenix, driven to the program's end

* **Beside the real game**: the user's three Phoenix screenshots of the
  race's start match the runtime's fields 7547, 7600 and 7740 once the
  grid is the same. The grid is chosen by the C library's `rand`, which the
  menus advance once a field (`GlueShell`'s `Random(2)`): taking the
  circuit at field 6356 instead of 6300 puts the player on the back row,
  5th, as in the user's run. The projector's one-pixel question stays
  below what Phoenix's scaled JPEGs show.
* **Driving**: A is the accelerator (the default control configuration,
  read in `TopOfFrame` and `CNBReadJoystick`); `pfboot --pad a@7700+40000`
  holds it (the user's choice: the game's own button, held). Held alone it
  takes the car three laps round, along the walls, to the line in 6th
  place.
* **After the race**: the music player's thread deleted (DeleteItem of a
  task, read in os_code), the Rankout screen ("3 CONTINUES REMAIN",
  CONTINUE and QUIT); CONTINUE runs the race again; QUIT unloads the
  instrument templates (`UnloadInsTemplate`, a template's deletion, read
  in AUDIOFOLIO), is refused a `SetFunction`, and the program returns 1 to
  the OS after 935,186 calls.
* **`pfboot --frames-at FIRST[-LAST][/EVERY]`**: frames of a long run
  without writing every field.
* **Checks**: the three traces byte for byte, self-test 0 failures, six
  memory runs, sixteen Graphics snapshots; the 2,687 fields to Select
  Circuit byte for byte against the previous build.
* **Where the run stops**: nowhere on the way it was driven -- from the
  boot through a race, the Rankout screen and QUIT, `launchme` runs to its
  own end.
* **The window** (after the wrap-up, the user's choice): `pfboot --window`
  shows the display in an SDL3 window in real time, with the keyboard
  (arrows, Z X C for A B C, Enter for P, Backspace for X, Q W for L R) and
  a gamepad as the pad; `--record FILE` writes the presses as `--pad`
  options that replay the run. `tools/play.cmd` starts it; the user was
  playing in the first test window before it was even announced.

## Session 14 (2026-10-08) — the guest's clock in the ARM60's clocks

* **What a safe point was worth**: an instruction-counting build (scratch
  only) and the ARM6 datasheet's cycles: a safe point stood for 19 clocks
  on a menu, 52 in the intro movie, 90 in the race, so at 1 us each the
  guest ran 1.5 to 7 times the console's speed.
* **The clock in clocks** (kit ca71e86): the emitter counts each block's
  clocks (an N cycle two, a failed condition one, a multiply's from rs),
  the runtime moves the clock on 80 ns a clock (12.5 MHz).
* **The movies**: the intro movie decodes its 24 frames a second in about
  half the console's CPU time and waits for each frame's time; it shows
  the same 349 pictures in 1200 fields before and after. Its smoothness
  against Phoenix is not the CPU's: Phoenix's own figures are still to
  measure.
* **The race** holds its 30 frames a second with the clock in clocks
  (about three quarters of each field's clocks used).
* **The grid moves** (`rand` goes once a loop on the logo movie): the
  user's Phoenix grid now comes with the circuit taken at 6405; then 7349,
  7549, A held from 7749; the race starts at about 7602 and its first
  fields are those that matched Phoenix, pixel for pixel. Rankout at
  40,560; QUIT ends the program after 808,823 calls.
* **Checks**: the battery byte for byte; self-test 0 failures; six memory
  runs; sixteen Graphics snapshots (the late ones renumbered 624 625 643
  2101 2102); Immercenary's and OMF2097's traces byte for byte,
  `launchme`'s but for the time of its first wait; the pictures to Select
  Circuit the same in the same order, one transition in fewer steps.
* **The user at par with Phoenix**: the window and Phoenix alike, the
  movies' slow-downs at the same places in both -- the file's own frame
  lengths (type-7 records: 2 fields plus 2 x N each).
* **The user's play** went through a whole race into the pits, and
  stopped at `MapCel` (kit 62c582d: as GRAPHIX does it, with its own
  division; the pit screen then works). The picture's first line was the
  OS's VIRS line, now left out (240 lines). The radar leaking left of its
  box is GRAPHIX's own `SetClipOrigin` refusing the game's origin (the
  clip still 320 wide): the real game should show it too.
