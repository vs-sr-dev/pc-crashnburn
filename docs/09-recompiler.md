# The recompiler

The translator is 3dokit's layer 4, written for this game and kept free of
it, in the manner of saturnkit's `recomp/`: Python that reads an AIF image
and writes C++ against a runtime header, one C++ function per guest
function. Session 2 designed it and wrote discovery; session 3 wrote the
rest, and `launchme` now recompiles whole, builds, and agrees with the
interpreter on every function that can run without the OS.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme+SEEDS --optest   # the seeds: below
python -m 3dokit.recomp.selftest --image launchme=build/disc/launchme --auto \
       --out build/recomp/selftest/launchme.txt
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build
build/recomp-build/selftest build/recomp/selftest/optest.txt build/recomp/selftest/launchme.txt
```

(CMake, Ninja and clang from MSYS2's mingw64, `C:\msys64\mingw64\bin`, put
on the path for those two commands only: its own Python has no capstone.)

## What the input is

* **ARM60**: ARMv3, 32-bit mode, big-endian, no Thumb, no halfword loads,
  no long multiply. Conditional execution on every instruction, the
  barrel shifter with its carry out, `ldm`/`stm` with writeback, `msr` on
  the flags.
* **APCS-3/32 with frame pointers and stack checking**, from Norcroft C,
  plus hand-written routines that take liberties the compiler never does:
  the routines at 0x39148 and 0x39400 load flags from data with
  `msr cpsr_f`, and the first uses `sp` as a plain register; 0x41fd8 and 0x42120 park their return
  address in a word of their own; 0x445d8 dispatches through the handler
  word before an object.
* **One image linked at 0** with 4,930 relocations. The runtime loads it at
  0 in the 3DO's own address space, so no relocation is applied and every
  constant in the data means what it meant on the console.

## The pieces (all in `3dokit/`)

| | |
|---|---|
| `arm60` | the instruction set, ARMv3 exactly (session 2) |
| `armemu` | the interpreter: the reference for every rule below. 8 known-answer tests of what the ARM60 does and an ARMv5 does not, and random instructions against unicorn's ARM926 (27,819 agree) |
| `recomp.discover` | functions, code and data, switches, indirect transfers (session 2; session 3 taught it the parked-lr return) |
| `recomp.emit` | an instruction as C++, a function as a C++ function |
| `python -m 3dokit.recomp` | a module per program: `p_<name>_NNN.cpp`, the table of entries, `modules.cpp`, `CMakeLists.txt`, `report.txt` |
| `recomp.selftest` | the interpreter records vectors, the C++ replays them |
| `runtime/arm60.h` | the CPU, memory, the shifter and the flags, as C++ |
| `runtime/arm_core.cpp` | guest memory, the active module, dispatch, the return check |
| `runtime/arm_stub.cpp` | no OS: every SWI and every call outside the program stops |
| `runtime/arm_selftest.cpp` | the replay |

## The ARM60's rules, as both sides follow them

* **An unaligned `ldr`** reads the aligned word and rotates it right by 8 x
  address[1:0]; big-endian, offsets 0 and 2 leave the addressed byte in
  bits 31-24, 1 and 3 in bits 15-8. `str`, `ldm`, `stm` ignore address[1:0].
  The C++ checks the alignment at run time (`ldw`); the branch is cheap and
  nothing has to prove alignment.
* **`pc` as an operand** is the address + 8, + 12 under a register shift;
  `str pc` and `stm {..., pc}` store + 12. The APCS prologue stores it.
* **`ldm` with the base in the list** and writeback keeps the loaded value;
  **`stm`** stores the base's original value when it is the lowest
  register, the written-back one otherwise.
* **`mul` with S** sets N and Z and leaves C and V (the datasheet's C is
  "meaningless": both sides leave it).
* **`msr cpsr_f`** writes the flags; **`mrs`** reads them over user mode.
* What user mode leaves unpredictable (an S on a write to pc, `ldm ^`,
  SPSR, writeback to pc, a load into the base it writes back) is refused by
  both: nothing in nine programs' reached code needs it.

## Emission

* **The CPU** is `ArmCpu`: `r[16]`, the flags N Z C V as four words, `pc`
  (where the last return went) and a poll budget. Memory is one 3 MB host
  array (DRAM at 0, VRAM at 0x200000), big-endian; anything outside goes to
  `arm_io_*`.
* **One C++ function per guest function**, `void f_XXXXXXXX(ArmCpu&)`, in
  namespace `p_launchme`; every instruction in address order in its own
  block, a label where something branches, a `goto` past a literal pool;
  a conditional instruction is an `if` on the flags. Every flag an
  instruction sets is computed (no liveness pass yet: clang removes much of
  it).
* **Calls**: `bl f` sets lr and calls `f_...`; the callee's return stores
  where it went in `c.pc` and returns, and the caller checks it is the word
  after the call (`ARM_RET`). A `b` to another function's entry is a tail
  call. `mov pc, lr`, `ldm ..., pc`, `ldr pc, [sp], #4` and the parked-lr
  `ldr pc` are returns.
* **The switch** is a C++ `switch` over its `b` table. Any other write to
  pc after `mov lr, pc` is a call through `arm_call` (a lookup in the
  entries); otherwise a jump through it, as a tail.
* **The OS**: `swi n` is `arm_swi(c, n)`; a folio vector is a call or tail
  jump through `arm_call` to whatever the folio's table holds in guest
  memory, which the runtime will make an address it maps to native code.
* **Safe points** (`ARM_POLL`) at backward branches and before calls.
* After `bne x; beq y` with the flags unchanged nothing runs on; the one
  place in `launchme` (0x4cf8, in the byte-copy routine at 0x4ce0) emits a fault
  there rather than a call.

`report.txt` for `launchme`: 553 functions, 43,805 instructions (22 words
shared by two functions), 1,831 calls, 729 returns, 259 SWIs, 16 switches,
11 indirect calls, 34 indirect jumps (32 of them folio vectors), and no
static target that is not an entry. 8 C++ files, built in about 6 seconds.

## The self-test

* **The instruction test** (`--optest`): a synthetic AIF image of 891
  functions, every data-processing operation with every operand2 form
  (immediates rotated and not, every immediate shift at its edges, every
  register shift, pc read at + 8 and + 12), the multiplies, single and
  block transfers in every addressing mode with unaligned words, `swp`,
  `msr`, `mrs`, each under a random condition, and sequences for the
  control flow (branches both ways, a loop, `bl` with an APCS frame, a
  conditional `bl` and return, a tail call, a call through a register,
  the switch, flags loaded by `msr`, a 64-bit add). 10,580 vectors, 0
  failures. Two faults injected by hand into the generated C++ (`sbc`'s
  borrow, the rotation of an unaligned `ldr`) failed hundreds of vectors
  and 77.
* **The game's functions** (`--auto`): those that return on random states
  without an OS call, without a fault, and without writing to the
  program's code -- 138 of 553, 35 of them with pointer arguments:
  `Arctan`, `Distance`, `Random`, `SortByD`, `CarCollision`,
  `NSquaredCheck`, `DivideRoadEdges`, the division routine at 0x160,
  the outcode routine at 0x41fd8... 2,083 vectors, 0 failures; under two other seeds,
  5,730 more.
* **Eight other programs** (`Orion`, Immercenary's six, OMF2097's
  `LaunchMe`) recompile with nothing refused and replay 1,016 functions,
  15,722 vectors, with 0 failures: the kit is not tuned to this game.

One finding on the way: a vector recorded after a function had written
into the code (on random pointers) ran changed code in the interpreter,
which the C++ cannot do. The recorder now refuses writes to code words.

## The indirect transfers, all eight

| site | in | what it is | emitted as |
|---|---|---|---|
| 0xf3b0 | `SpliceInOneObject` | `mov lr, pc; ldr pc, [r4, #0x1c]`: an object's handler | call through `arm_call` |
| 0x19b68 | `DoEnemyAi` | `ldmdb fp, {r5, fp, sp, lr}` then `ldr pc, [r1, r0, lsl #2]`: the frame undone, a tail jump through the drivers' table at 0x5cfb0 (Fang, Druger, TasmanTwix, MaxAmillion, Klaw, Rocker, three empty slots, Drone: all relocated entries) | tail jump through `arm_call` |
| 0x37694 | 0x37668, called by `main` | `mov lr, pc; ldr pc, [r4, #0x104]`: an object's state machine (seeds below) | call through `arm_call` |
| 0x41fec, 0x4203c, 0x42068 | 0x41fd8 | `ldr pc, [lr]` with lr pointed at 0x41fd4, where the routine stored its lr on entry | returns |
| 0x42328 | 0x42120 | `ldr pc, [ip]`, ip = 0x42118, where it stored its lr | return |
| 0x4495c | 0x445d8 | `mov pc, r3`, r3 the word before an object: its handler. The 10 relocated words that point into this routine (0x5823c...) all point at its start; the handlers are the routine's later entries (seeds below) | tail jump through `arm_call` |

## Entries only data reaches: the seeds

Discovery seeds a function from a relocated word only when the word points
at an APCS prologue or an embedded name. Some of the game's code is reached
from nothing else: leaf routines without a frame, whose address is a
literal stored into an object or kept in a data structure. The runtime
stops on the first call to one ("a call to an address that is no
function's entry"); the port names them on the command line
(`launchme=FILE+SEED,...`, `3dokit.recomp`), 22 of them, found in session
12 on the way to the race:

* **The objects' state machines**: eight three-word dispatchers, `ldr r0,
  =table; ldr r1, [r4, #0x108]; ldr pc, [r0, r1, lsl #2]` -- the object's
  state word indexes its kind's table of handlers -- at 0x154b4, 0x158fc,
  0x19530, 0x250f8, 0x25abc, 0x26780, 0x27908, 0x27cec; a constructor
  stores one in the object's word +0x104 (0x15414: `ldr r1, =0x154b4; str
  r1, [r0, #0x104]`), and 0x37668 calls it each frame. One more +0x104
  handler, 0x26fec, is not a dispatcher. The tables' handlers are named
  functions but for 0x5ba94's three, frameless leaves: 0x19540, 0x195bc,
  0x195dc.
* **A callback**: 0x2f314, `mov r0, #0; mov pc, lr`, passed in r3 at
  0x2e974 and 0x2eb2c.
* **The models' handlers** in the hand-written 0x445d8: nine entries into
  its unrolled run of faces, one step per bit of a face mask (`tst ip,
  #bit; blne 0x444f8`), each kept in the word before a model's data
  (0x45f54, 0x48c58, 0x4ddd4, 0x52764, 0x4b5bc, 0x5061c, 0x54b38, 0x562b8,
  0x56670): 0x449a8, 0x44fb0, 0x44fcc, 0x45058, 0x450c8, 0x45138, 0x451fc,
  0x45564, 0x45648.

A scan of every relocated word and every literal loaded by reached code
that points at an unreached word of the code range, with a trial descent
from each, finds these; every other target whose descent runs cleanly is
data of zeros and small numbers, which decode as `andeq` and run on for
hundreds of words (the buffers at 0x37a58 on and 0x42894 on, the tables at
0x31d2c and 0x376ac). A rule general enough to find the routines in the
kit would take that data too, so the list stays the port's.

```sh
python -m 3dokit.recomp --out build/recomp --optest \
  "launchme=build/disc/launchme+154b4,158fc,19530,19540,195bc,195dc,250f8,25abc,26780,26fec,27908,27cec,2f314,449a8,44fb0,44fcc,45058,450c8,45138,451fc,45564,45648"
```

575 functions with the 22 seeds, 553 without.

## What is left

* **The OS** (phase 4 of `06-attack-plan.md`): begun at the end of the
  session as a frame (`3dokit/runtime/pf*`, the `pfboot` target): the boot,
  the OS's memory above VRAM, folio tables of trap addresses, every SWI
  and slot dispatched and traced by its SDK name. `kprintf` and the
  startup's slot -120 are its only functions so far.
* **Speed**: the flags' liveness, literal pools folded into constants.
* **Returns that are not to their call** (a longjmp, the startup's
  hand-over): `ARM_RET` stops on them; none is met yet.
* **Ghidra's function list** against discovery's (`--against`): not done;
  the self-test and the nine programs are the stronger check now.
