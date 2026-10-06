# Next session: naming the OS surface, and the oracle

Where things stand: the kit reads the disc and maps the code
(`03-executables.md`); the route is chosen (`06-attack-plan.md`). Nothing
is translated yet.

## The work

1. **The SDK's headers as a reference.** Clone trapexit's `3do-devkit`
   (headers and libraries of the 3DO SDK) outside the repositories, e.g.
   `D:\Homebrew6\refs\3do-devkit`, read only: the SWI numbers and the
   folio vector slots of the Kernel, Graphics, audio, File and Operamath
   folios. Check them against this disc's OS (v0.16, 1993) before
   trusting them: numbers may have moved between releases.
2. **Name the surface** in `3dokit.portfolio`'s tables: the 35 SWIs and
   the 75 + 38 vector slots of `launchme`, each name checked at its call
   sites (arguments, use of the result) in the game's code, whose
   functions are named.
3. **The libraries.** Name the 292 functions the compiler did not name
   (the libraries linked after 0x2d2f4 -- C library, graphics.lib, audio
   glue -- and any hand-written routines; where each lies is to be
   counted) with `3dokit.shapes`
   against the devkit's `.lib` objects, where their shapes match the 1993
   build; the rest by hand. Kept as a symbol file in `tools/`.
4. **The oracle.** `tools/oracle.py`: RetroArch + `opera_libretro`
   headless, the disc, screenshots at given frames and a recording, as
   pc-deepfear's. A first run: what the game shows in its first 30
   seconds (logos, the movie, the menu), to set the targets of phase 5.
5. **The translator's design** written in `09-recompiler.md`, in the
   manner of saturnkit's `recomp/` (`discover`, `emit`, `selftest`), and
   a first `3dokit.recomp.discover` on `launchme`, compared with Ghidra's
   function list (`ghidra/ExportFuncs.java`).

## Keep in mind

* Every 3dokit change is checked on Immercenary's and OMF2097's discs
  (`aif --scan`, `dsp --verify`, `cel --check`, `arm --stats` before and
  after) and recorded in `10-3dokit.md`; commit in the kit, then
  `git pull --ff-only` in the submodule and commit the port.
* The disc is `iso/Crash n Burn (USA Korea).cue` (a copy of the
  documentation pipeline's `_work/cnb.bin`, sha1 8702aaf8...); the
  extracted tree is `build/disc` (`python -m 3dokit.disc ... --extract
  build/disc`).
* Opera's source is a reference for the CEL engine and the OS's
  behaviour: read, never copied (LGPL).
