# The recompiler

The translator is 3dokit's layer 4, written for this game and kept free of
it, in the manner of saturnkit's `recomp/`: Python that reads an AIF image
and writes C++ against a runtime header, one C++ function per guest
function. Session 2 designed it and wrote discovery; session 3 wrote the
rest, and `launchme` now recompiles whole, builds, and agrees with the
interpreter on every function that can run without the OS.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
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
| 0x37694 | 0x37668, called by `main` | `mov lr, pc; ldr pc, [r4, #0x104]` | call through `arm_call` |
| 0x41fec, 0x4203c, 0x42068 | 0x41fd8 | `ldr pc, [lr]` with lr pointed at 0x41fd4, where the routine stored its lr on entry | returns |
| 0x42328 | 0x42120 | `ldr pc, [ip]`, ip = 0x42118, where it stored its lr | return |
| 0x4495c | 0x445d8 | `mov pc, r3`, r3 the word before an object: its handler. The 10 relocated words that point into this routine (0x5823c...) all point at its start | tail jump through `arm_call` |

## What is left

* **The OS** (phase 4 of `06-attack-plan.md`): `arm_stub` stops at the
  first SWI; Portfolio at the folio boundary is the next layer, with the
  folio tables as structures in guest memory.
* **Speed**: the flags' liveness, literal pools folded into constants.
* **Returns that are not to their call** (a longjmp, the startup's
  hand-over): `ARM_RET` stops on them; none is met yet.
* **Ghidra's function list** against discovery's (`--against`): not done;
  the self-test and the nine programs are the stronger check now.
