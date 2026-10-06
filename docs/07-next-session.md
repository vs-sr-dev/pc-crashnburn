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
2. `ChangeDirectory("$boot")` (swi 0x30007, in `InitHardware`): the File
   folio's current directory; `$boot` is the disc the program came from.
3. `FindItem(0x104, tags)` (swi 0x10004, at 0x2ebbc): a folio by name, the
   tags on the stack (`{1, name}`, then 0). Then `OpenItem`, then Kernel
   -48 `LookupItem` for the folio's node, whose negative offsets are its
   vector table (`pf_folio_base`). After that, with `--lenient`, `FindMH`.

So the first piece is **items**: a table of item numbers to nodes in the
OS's memory, the folios registered as items of type 0x104 with their
names (Graphics, audio, File, Operamath), `FindItem` by type and tags,
`OpenItem`/`CloseItem`, `LookupItem`, `CheckItem`, `IsItemOpened`. Then
what `--lenient` shows next. `03-executables.md` lists everything the
game reaches: 33 SWIs, Graphics 14 slots, Kernel 11, audio 12, File 4.

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
