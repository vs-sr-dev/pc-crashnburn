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
