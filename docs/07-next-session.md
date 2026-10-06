# Next session: the emitter, and an interpreter to check it

Where things stand: every OS call the game reaches is named (33 SWIs, 41
folio slots, `03-executables.md`); `3dokit.arm60` decodes ARMv3 exactly and
`3dokit.recomp.discover` finds launchme's 553 functions with 0 descents
into data. Phoenix runs the game and is the reference; Opera does not
(`08-oracle.md`). Nothing is translated yet.

## The work (`09-recompiler.md`)

1. **`3dokit.armemu`**: an ARM60 interpreter in Python over `arm60`'s
   decoding -- the reference for the shifter, the flags, `ldm`/`stm`, the
   unaligned `ldr`'s rotation -- with tests of its own.
2. **`3dokit.recomp.emit`**: C++ per function against a CPU header (in
   `3dokit/runtime/`, next to the C99 readers), switches as `switch`,
   indirect transfers through the table of every function start; first
   one small function, then all; `python -m 3dokit.recomp` writes
   `build/recomp/` with its CMakeLists.
3. **`3dokit.recomp.selftest`**: each function through the interpreter
   and through the compiled C++, calls and OS calls stubbed, registers,
   flags and memory compared.
4. **The 8 non-OS indirect transfers** one by one: the drivers' AI table
   (`DoEnemyAi`), `SpliceInOneObject` and 0x37694's pointer calls, the two
   library routines that load `pc` from `[lr]` (0x41fd8, 0x42120: what
   follows their callers), and the hand-written routine at 0x445d8 (what
   it is, who reaches it).
5. Ghidra's function list against `recomp.discover` (`--against`), with
   `ghidra/ExportFuncs.java` from saturnkit adapted.

## Questions for the user

* On Phoenix: does the game's `kprintf` output show anywhere (its
  debugger, a log window)? It would be the runtime's first comparison.
* On the console (when convenient): the same start as Phoenix's?

## Keep in mind

* Every 3dokit change is checked on Immercenary's five programs and
  OMF2097's LaunchMe (`aif --scan`, `dsp --verify`, `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report`, before and after) and
  recorded in `10-3dokit.md`; commit in the kit, `git pull --ff-only` in
  the submodule, commit the port.
* Discs: `iso/Crash n Burn (USA Korea).cue` and `iso/disc-E.iso` (the
  user's pressing, identical); the extracted tree is `build/disc`.
* The SDK reference is `D:\Homebrew6\refs\3do-devkit` (read only).
* Write Python that has backslashes or quotes in it with the Write tool,
  never through a shell heredoc.
