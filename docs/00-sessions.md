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
