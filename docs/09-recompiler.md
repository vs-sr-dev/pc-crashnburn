# The recompiler: design

The translator is 3dokit's layer 4, written for this game and kept free of
it, in the manner of saturnkit's and wiikit's `recomp/`: Python that reads
an AIF image and writes C++ against a runtime header, one C++ function per
guest function. This page is the design; nothing of it is written yet.

## What the input is

* **ARM60**: ARMv3, 32-bit mode, big-endian, no Thumb, no halfword loads
  (`ldrh`/`strh` are ARMv4), no long multiply (`umull`... are ARMv3M; 200
  words that decode as them in `launchme` are data). Conditional execution
  on every instruction, the barrel shifter with its carry out, `ldm`/`stm`
  with writeback, `swp` (none in `launchme`), `mrs`/`msr` (7 decoded, to be
  checked as code or data).
* **Unaligned `ldr`** rotates the word on ARMv3; `ldrb`/`strb` are plain.
  The emitter rotates only where the address is not provably aligned (a
  `ldr` off `sp`, `fp`, or a literal is aligned).
* **APCS-3/32 with frame pointers and stack checking**: `mov ip, sp;
  stmfd sp!, {..., fp, ip, lr, pc}; sub fp, ip, #4; cmp sp, sl; bllt
  __rt_stkovf`, returns by `ldmdb fp, {..., fp, sp, pc}` or `mov pc, lr`.
* **One image linked at 0** with 4,930 relocations. The runtime loads it
  at 0 in the 3DO's own address space, so no relocation is applied and
  every constant in the data means what it meant on the console.

## Discovery

From `3dokit.arm.Image`, `3dokit.aif` and `3dokit.portfolio`:

1. **Function starts**: APCS prologues, `bl` targets, the compiler's
   embedded names (292), the relocation list's words that point into code
   (the 45 targets of the pointer tables), callbacks handed to the OS
   (`CreateThread`'s entry, `SetFunction`'s function), and the AIF entry.
2. **Code vs data in the read-only area.** The compiler parks literal
   pools, strings and `const` tables in the code; the linker puts the
   libraries' read-only data after the code. A function's body is what
   control flow reaches from its start (`arm.Image.reached` without
   orphans), stopping at returns and unconditional branches; what is not
   reached is data. The `svcne #0` "functions" at 0x39548, 0x4437c and
   0x44408 are the warning: a `blne` decoded from data must not make a
   function, so a `bl` target counts only when the `bl` itself is reached.
3. **Switches**: `cmp rN, #n; addls pc, pc, rN, lsl #2; b default; b
   case0; ...; b case(n)` -- 17 of them; the table is the n+1 branches after
   the `b default`.
4. **Indirect jumps**: `mov pc, lr` and `ldm ..., pc` are returns;
   `ldr pc, [rB, #-slot]` with `rB` loaded from a folio's global is an OS
   call; any other `ldr pc`/`mov pc, rN` is a dispatch through the table of
   all function starts, which faults loudly on a miss.
5. **Checked against Ghidra** (`ghidra/ExportFuncs.java`, as saturnkit's
   and xboxkit's) and against the embedded names: every named function
   must be found, with the size the next name implies.

## Emission

* A CPU struct: `r[16]`, the flags N Z C V as separate bytes, `sl`/`fp`/`sp`
  as registers like any other. Memory is one 4 MB host array mirroring the
  3DO's map (2 MB DRAM at 0, 1 MB VRAM at 0x200000), big-endian; loads and
  stores byte-swap, with a bounds check in debug builds.
* **One C++ function per guest function**, `void f_0001234(Cpu&)`; basic
  blocks as labels, branches as `goto`, conditional instructions as `if`
  on the flags; flags computed only where a later instruction reads them
  before they are written again (a per-block liveness pass).
* **Calls**: `bl f` is `f(cpu)` with `lr` set to the return address (the
  code reads `lr` in the prologue's `stmfd`), and the return is a C++
  return. `ldm ..., pc` and `mov pc, lr` return; a function that returns to
  an `lr` other than its caller's (setjmp/longjmp, the startup's
  hand-over to `main`) is handled by checking `pc` after each call against
  the expected return address and unwinding if it differs.
* **OS boundary**: `swi n` calls `os_swi(cpu, n)`; a load of `pc` from a
  folio's table lands, through the fake folio tables in guest memory, on
  an address the dispatcher maps to `os_slot(cpu, folio, slot)`. Unnamed
  or unimplemented numbers stop with their name and call site.
* **Output**: `build/recomp/p_<name>_NNN.cpp` split by size, `funcs.cpp`
  (the address table), a generated `CMakeLists.txt` including
  `3dokit/runtime/runtime.cmake`, and `report.txt`.

## Self-test

An ARM60 interpreter in Python (`3dokit.armemu`, as `saturnkit.sh2emu`):
for every function, random registers and a random memory window are run
through the interpreter and through the recompiled function (calls and OS
calls stubbed to record their arguments), and the registers, flags and
memory compared. It doubles as the reference for the barrel shifter and
the flags.

## Order of work

1. `recomp.discover` with its report and the Ghidra comparison.
2. `armemu` with tests of its own (shifter, flags, ldm/stm, the unaligned
   rotate).
3. `recomp.emit` for one function, then all; the self-test.
4. The runtime skeleton (phase 4 of `06-attack-plan.md`) links it.
