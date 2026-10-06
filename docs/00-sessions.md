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
