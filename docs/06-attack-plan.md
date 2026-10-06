# The porting route

## Verdict: feasible, by static recompilation, and the most favourable 3DO case yet seen

| Road | Meaning | Verdict |
|---|---|---|
| Reimplementation | a new engine reading the assets | No: half the disc is in formats nobody has derived (`.sc`, `.mr`, the type-4 `BIGFILE` members, two opcodes of the movie codec), and the game's logic lives in 292 functions plus the libraries. Immercenary went this way and after 20+ sessions has a viewer, not a game |
| Decompilation | rebuild C source and compile it for PC | No: the same functions, by hand |
| Enhanced emulation | an emulator with more speed | Not a port, and LGPL code. Opera (libretro) is the oracle only |
| **Static recompilation** | the ARM60 code to C++, Portfolio and the hardware reimplemented | **Yes** |

Why it is favourable here, every point measured on the disc
(`03-executables.md`):

1. **One program, small.** `/launchme` is 433,928 bytes: 279,780 of code
   and read-only data, 134,236 of data, 22,096 of BSS. 584 functions, about
   70,000 words of which some are literal pools. Immercenary's main
   program alone is 1,308 functions.
2. **It names itself.** The compiler left every one of the game's **292
   functions named** in the code (`main`, `DrawRoad`, `MoveEnemyCar`,
   `FMV_DecompressFrame`, `_MEDPlayer`...). The other 292 are mostly the
   linked SDK libraries after 0x2d2f4, the same on every game of the SDK,
   so their names are learnt once for the kit.
3. **The call graph closes statically.** ARM60 has no delay slots. Every
   jump that writes `pc` in reached code is one of four kinds, all
   bounded: 114 `mov pc, lr` returns; 116 folio vector calls (the OS
   boundary, all found by `portfolio`); **17 switches** in the compiler's
   form (`addls pc, pc, rN, lsl #2` then a run of `b`, its size set by the
   `cmp` before it: a C `switch`); and 15 calls through **pointer tables in
   the data** (drivers' AI, weapons, the car's init/move, death
   animations), whose 45 possible targets are found exactly through the
   AIF relocation list.
4. **No hardware is touched directly.** No ROM, MADAM or CLIO address is
   loaded or built by reached code, as a literal or as an immediate; drawing, sound, files, the pad and
   timing all go through Portfolio's folios and devices. The cut is
   clean: **HLE at the folio boundary**, not register-level emulation.
5. **The hard formats need no decoding.** The movies (a codec of the
   studio's own, `FMV_DecompressFrame`), the music (ProTracker modules
   played by the game's own `_MEDPlayer`), the tracks (`.sc`, `.mr`): all
   decoded by the game's code, recompiled like the rest. The open
   questions of the documentation pipeline do not block the port.
6. **The sound is four DSP instruments.** The game names only
   `varmono8` (a voice of the module player), `mixer8x2`, `sampler` and
   `dcsqxdhalfmono` (SDX2). These are reimplemented by name as native
   mixers, no DSP emulation needed.
7. **No Cinepak, no DataStream.** The SDK's heaviest libraries are not
   linked.

What is new, and so harder:

1. **3dokit has no layer 4 or 5 yet.** The ARM60-to-C++ translator, the
   Portfolio HLE and the CEL engine are all to be written. They are the
   kit's, not this port's: every later 3DO game reuses them.
2. **The CEL engine.** Every pixel on the 3DO is a cel drawn onto a
   quadrilateral (HDX/HDY/VDX/VDY/HDDX/HDDY), through the pixel processor
   (PIXC, the PPMP blends). The game is a 3D racer: its road and cars
   are cels mapped as quads, so the mapping, the blends and the clipping
   must be right. It is the largest single piece, as the kit's README
   already says.
3. **The 1993 OS.** `os_code` is v0.16 by its ROM tag, older than
   anything the kit has read (Immercenary is 23.10). The audio folio is
   reached by SWIs here (folio 4: 10 entry points), not only by vectors.
   SWI and slot numbers must be checked against this OS, not assumed from
   later ones.
4. **Asynchronous I/O.** The game streams track data while it runs
   (`ASYNC_LoadSomeMore`, `CDIO_ASYNCRead`, `SendIO`, `WaitSignal`), on
   its own buffer system. The HLE's CD device must honour the IOReq,
   signal and message semantics, and timing must be plausible.
5. **A second program.** `/Orion`, the `blazer` preview (156 functions,
   47 named), runs from the scripts' loop between demo and game. It comes
   free once the translator works, but is not the target.

## Where to cut

The same principle as the other kits: *cut at the hardware where the
hardware is the interface* -- and here the interface is Portfolio.

| Layer | Inside the recompiled code | Reimplemented natively |
|---|---|---|
| Game logic, maths, the movie decoder, the module player, track streaming | everything in `/launchme`, game and SDK libraries alike | -- |
| Kernel | the C library, the SDK glue | SWIs (signals, messages, items, memory, tasks) and Kernel folio vectors |
| Graphics | graphics.lib wrappers | the Graphics folio's 38 vector slots: screen groups, bitmaps, VDLs, `DrawCels`/`DrawScreenCels`, `DisplayScreen`, `SetCEControl`; the CEL engine behind them |
| Audio | the module player, `LoadInstrument` callers | audio folio SWIs and vectors: instruments by name, samples, knobs, start/stop, timers (`AudioTime`) |
| File and devices | `CDIO_*`, `DiskSound_*` | File folio, the CD device's IOReqs on the disc image via `3dokit.disc`, `SPORT` (VRAM copies and clears), `timer`, the control port (pad), `/nvram` as a host folder |

Memory is the 3DO's own: 2 MB of DRAM at 0 and 1 MB of VRAM at 0x200000,
big-endian, one flat array, so the game's pointers mean what they meant.
The OS allocates from it in the HLE (the game asks for VRAM by type and
uses the address for its screens), and the folios' tables are fake
structures in it whose vector slots point at addresses the dispatcher maps
to native functions.

## The translator (3dokit layer 4), in saturnkit's manner

* **Discovery** from `arm.Image` (function starts, calls, tail calls,
  `reached`), the AIF relocation list (pointer-table targets, and which
  words are addresses), the embedded names, and `portfolio` (where the
  OS is called). Checked against Ghidra's function list.
* **Emission**: one C++ function per guest function, registers and
  flags in a CPU struct, `bl` a direct call, `ldm ..., pc` and
  `mov pc, lr` a return, the compiler's switch a C `switch`, an
  `ldr pc, ...` through a data pointer a lookup in the table of every
  function start (so a pointer from the data lands on its C++ twin), a
  `swi` or a folio vector a call into the HLE. Conditional execution on
  every instruction, the barrel shifter with its carry, ARMv3 rules
  (rotated unaligned `ldr`, no halfword loads, no long multiply, no
  Thumb).
* **Self-test** against an ARM interpreter written for the kit (as
  `sh2emu.py` is saturnkit's): random registers and memory through each
  function, recompiled against interpreted.

## The oracle

Phoenix 2.8, which runs the game; Opera (libretro) does not get past the
start (`08-oracle.md`). Emulators are read, never copied.

## Phases

| # | Phase | Done when |
|---|---|---|
| 1 | Survey: disc, code, OS surface, the kit split out | **session 1** |
| 2 | Name the OS surface: every SWI and slot of `launchme` against the SDK's headers and the oracle | 35 SWIs and 75+38 slots named, in `portfolio`'s tables |
| 3 | Translator: discovery, emission, ARM60 interpreter, self-test | `launchme` recompiles, links against a stub runtime, self-test clean |
| 4 | Runtime skeleton: memory, kernel (items, signals, messages, tasks as cooperative fibers), File folio, CD device, a frame loop | `main` runs to the first `DisplayScreen`, logging the OS calls in the oracle's order |
| 5 | Graphics: screen groups, VDLs, the CEL engine in software at 320x240 | the logos and menus as the oracle's, pixel for pixel |
| 6 | Audio: the four instruments, the module player's voices, SFX | the menu music and effects as the oracle's |
| 7 | In game: pad, timers, async track loading, the movies | a race played start to finish; the user plays it |
| 8 | PC side: widescreen and higher resolution through the cel engine, frame pacing, saves | at the user's word |
