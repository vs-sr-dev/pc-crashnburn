# Next session: Portfolio, from the first call on

Where things stand: the translator is whole (`09-recompiler.md`).
`launchme` recompiles to C++, builds, and agrees with the interpreter on
every function that runs without the OS. On 3dokit's Portfolio frame
(`3dokit/runtime/pf*`, `pfboot`) it boots, prints `...cnb...`, and stops at
the first OS call not implemented. Phase 4 of `06-attack-plan.md` is the
work: `main` running to its first `DisplayScreen`, its OS calls in the
oracle's order.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient]
```

## The calls, in the order the game makes them

1. Kernel -120 (the startup's; handed through) and `kprintf` -- done.
2. `ChangeDirectory("$boot")` (swi 0x30007, in `InitHardware`): `$boot` is
   the disc the program came from, its root here -- done.
3. `FindItem(0x104, {TAG_ITEM_NAME, "Graphics"})` (swi 0x10004, at
   0x2ebbc), `OpenItem`, Kernel -48 `LookupItem`: the folio's node, whose
   negative offsets are its vector table -- done (items, end of session 3).
4. **Kernel -100 `FindMH`**, from the library stub at 0x3ec, with r0 = 0
   and r1 = 0x6497c: where the run stops. It belongs to the memory lists
   (`AllocMemFromMemLists`, `FreeMemToMemLists`, `ControlMem`): the next
   piece is **memory** -- the task's memory lists over free DRAM and VRAM,
   in the SDK's `MemHdr`/`MemList` layout where the game reads them.

Then what `--lenient` shows next. `03-executables.md` lists everything
the game reaches: 33 SWIs, Graphics 14 slots, Kernel 11, audio 12, File 4.
Items still to do as the game needs them: `CheckItem`, `IsItemOpened`,
`CreateSizedItem`, `DeleteItem`, and the devices found by name (`SPORT`,
`timer`, `mac`).

## Keep in mind

* What the OS's structures hold (Item, Folio, Task, IOReq, MemHdr...) is
  the SDK's headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`): where
  the game reads a field directly, `--trace 2` shows the access, and the
  field must be where the 1993 headers put it.
* Memory: the OS must hand out DRAM and VRAM (`AllocMemFromMemLists`,
  `ControlMem`, the game's own banks "Kernel VRAM", "Task's VRAM", "Bank
  2/3 (VRAM)"): free DRAM is after the program's BSS (0x6a790) up to the
  stack (64 KB under 0x200000), VRAM is 0x200000-0x2fffff.
* `--lenient` is a preview, not a run to trust: an unimplemented call that
  returns 0 sends the game down paths it never takes on the console.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only:
  it exposes no debug output, so the order of OS calls and `kprintf`
  messages is checked against the game's code, not against a log.
* Every 3dokit change: the regression battery on Immercenary's six
  programs, OMF2097's `LaunchMe` and Crash 'n Burn's two (`aif --scan`,
  `dsp --verify`, `portfolio --sites`, `arm60 --check`, `recomp.discover
  --report`, `arm --names`), the self-test of all nine, recorded in
  `10-3dokit.md`; commit in the kit, `git pull --ff-only` in the
  submodule, commit the port.
* Write Python that has backslashes in it with the Write tool, never
  through a shell heredoc (session 3 met this again).

## Questions for the user

* On the console (when convenient): the same start as Phoenix's?

## Later, not next

* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
