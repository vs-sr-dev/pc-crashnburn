# pc-crashnburn

Toward a native PC port of **Crash 'n Burn** (3DO, 1993, Crystal
Dynamics), the combat racer that was sold with the console on its launch
day: twelve circuits, armed cars, a garage between races, and eight to
twelve minutes of full-motion video. It was released only on the 3DO and never
re-released. The goal is the game running natively on PC, by static
recompilation: at the speed it was made for, with instant loading, and
sharper where the hardware allows it.

This repository documents the code and grows the tooling for the port.
The disc itself is measured in the documentation pipeline,
[3do-crashnburn-doc](https://github.com/vs-sr-dev/3do-crashnburn-doc). It is
the second port built on **3dokit**, the game-agnostic toolkit for 3DO
reverse engineering that grew out of
[pc-immercenary](https://github.com/vs-sr-dev/pc-immercenary), and the
first to recompile 3DO code. 3dokit is taken here as a submodule: clone
with `--recursive`, or run `git submodule update --init`.

## BYOA — Bring Your Own Assets

This repository contains **documentation and tools only**. No game data, no
executables, no assets. You need your own original disc. The work is done
on the USA/Korea release, one data track, as a .cue/.bin set in `iso/`.

## Layout

    docs/            code analysis, the plan, the sessions
    3dokit/          game-agnostic 3DO toolkit (submodule)
    iso/, build/     your disc and everything derived from it (ignored by git)

## Tools

The Python tools need Python 3.8+, and capstone for the code. Run from the
repository root.

```sh
D="iso/Crash n Burn (USA Korea).cue"

# the disc: volume, ROM tags, every copy compared; extract it
python -m 3dokit.disc "$D"
python -m 3dokit.disc "$D" --verify
python -m 3dokit.disc "$D" --extract build/disc

# the executables, the pictures, the sound
python -m 3dokit.aif --scan build/disc
python -m 3dokit.cel --check build/disc
python -m 3dokit.audio --scan build/disc
python -m 3dokit.dsp build/disc/System/Audio/dsp --used build/disc/launchme

# the code: the compiler's names, the call graph, the OS surface
python -m 3dokit.arm build/disc/launchme --names
python -m 3dokit.arm build/disc/launchme --stats
python -m 3dokit.arm build/disc/launchme -d 644 -n 60          # main
python -m 3dokit.portfolio build/disc/launchme --sites

# the recompiler: C++ for the whole program, and its self-test
python -m 3dokit.recomp --out build/recomp --optest \
  "launchme=build/disc/launchme+154b4,158fc,19530,19540,195bc,195dc,250f8,25abc,26780,26fec,27908,27cec,2f314,449a8,44fb0,44fcc,45058,450c8,45138,451fc,45564,45648"
                                       # the seeds: entries only data reaches (docs/09)
python -m 3dokit.recomp.selftest --image launchme=build/disc/launchme --auto        --out build/recomp/selftest/launchme.txt
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build
build/recomp-build/selftest build/recomp/selftest/*.txt
```

Building the C++ needs CMake, Ninja and clang (MSYS2's mingw64).

## Status

**Session 1**: 3dokit split out of pc-immercenary into a repository of
its own and taken here as a submodule; it reads this disc, with three
changes (the AIF relocation stub, the DSP format's version 1, the
compiler's embedded function names). The code is surveyed: one program of
584 functions, the game's 292 named by the compiler, every indirect jump
bounded, no hardware access, all of the OS through Portfolio's folios. The
route is static recompilation with the OS reimplemented at the folio
boundary (`docs/06-attack-plan.md`).

**Session 2**: every OS call the game reaches named (33 SWIs, 41 folio
slots); the instruction set decoded exactly and the functions discovered;
Phoenix runs the game and is the oracle.

**Session 3**: the translator is whole. An ARM60 interpreter as the
reference, the C++ emitter, and a self-test: `launchme` recompiles to C++
(553 functions, 43,805 instructions), builds, and agrees with the
interpreter on an instruction test of 891 functions and on the 138 game
functions that run without the OS, with 0 failures
(`docs/09-recompiler.md`). The OS is begun: on 3dokit's Portfolio frame
(`pfboot`) the game boots, prints its banner, opens the Graphics folio,
and stops at the first call not yet implemented (`FindMH`, the memory
lists).

## Documentation

| | |
|---|---|
| [00-sessions](docs/00-sessions.md) | what each session did |
| [03-executables](docs/03-executables.md) | the programs, the code, the OS surface |
| [06-attack-plan](docs/06-attack-plan.md) | the route, where to cut, the phases |
| [08-oracle](docs/08-oracle.md) | what the port is compared with: Phoenix, not Opera |
| [09-recompiler](docs/09-recompiler.md) | the translator's design |
| [07-next-session](docs/07-next-session.md) | where the next session starts |
| [10-3dokit](docs/10-3dokit.md) | what this port gave 3dokit |

## Licence

MIT -- see [LICENSE](LICENSE). Crash 'n Burn is © 1993 Crystal Dynamics;
this repository contains none of it.
