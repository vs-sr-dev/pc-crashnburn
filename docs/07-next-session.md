# Next session: time, and the File folio's streams

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, makes its two screens as the
1993 GRAPHIX makes them, clears them with the SPORT device, builds its
whole mixer as the 1993 audio folio makes it (four templates from the
disc, the mixer, eight voices with their knobs and gains, 59 samples:
`03-executables.md`, "The sound's set-up"), and starts its sound thread,
which runs on a host thread of its own, allocates its signal, raises its
priority and waits (`03-executables.md`, "The sound thread"). The game
then stops at its 218th call, the first not implemented: **audio -76
`OwnAudioClock`**. What follows asks for time, then files.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient] [--max-calls N] [--disc DIR]
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before and after
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Folios/AUDIOFOLIO audiofolio.bin   # linked at 0
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin         # linked at 0x10000
```

## The calls, in the order the game makes them (`--lenient` preview)

1. Up to the sound thread's `WaitSignal` -- done (calls 1 to 217).
2. **The audio clock** (0x2c278): `OwnAudioClock` (audio -76),
   `GetAudioRate` (-60), `SetAudioRate` (SWI 0xf; the preview shows
   0x800000 as its second argument). Read them in AUDIOFOLIO
   (`03-executables.md` has its tables: vectors at 0xbfa4, slot -4 last;
   SWI n at 0xbf24 + 4 * (31 - n)); the clock is the folio's timer, and
   `SleepUntilTime`/`GetAudioTime` follow it later.
3. `FindItem(MKNODEID(1, 10), "eventbroker")`: a message port. The
   runtime has none and returns NOTFOUND, and the game goes on; on the
   console the OS starts `System/Tasks/eventbroker` (on this disc), so the
   game finds it there -- the controller probably comes through it. To
   be read before input.
4. `AllocMemFromMemLists` of 0x48000 bytes, `FindItem`/`OpenItem` of the
   File folio, then **File -4 `OpenDiskStream`** of thirteen sound effects
   (`CNBSFX/gun.sfx` ... `engine1.sfx`, 0x64338 on, from `LoadSFX`), then
   `Loading two universal graphics files` and `CNB/Glue/Chars.bin`
   (`BAD READ` and `InitHardare failed` in the preview, where every call
   returns 0). The disc's files are reachable now (`pf_host_path`): the
   File folio's streams are 1993 code too (`System/Kernel/os_code`? the
   File folio is not among `System/Folios` -- find where it lives first).

## Time

Nothing in the runtime advances yet. What will need it, all at once:
the audio clock and `SleepUntilTime`; the `timer` device (Immercenary's
`p` asks for it at its 18th call); the vertical blank the SPORT copies
wait for and `DisplayScreen` pairs with; the kernel's quantum, which would
also let equal priorities take turns. A host clock and a rule for when a
waiting task wakes is the decision of the session; with every task
waiting, the runtime stops with "every task waits" today.

## Keep in mind

* **A Graphics call is checked by replaying it on GRAPHIX** (`pfboot --snap
  N DIR`, then `pfcheck ... --graphix`); eleven pass byte for byte. The
  audio folio's calls cannot be replayed that way: its items hold its
  private DSP bookkeeping, which the game never reads.
* **Tasks** (`3dokit/runtime/pf_task.cpp`): one host thread each, one
  running at a time; a switch only where the 1993 kernel makes one at an
  OS call (a signal to a higher-priority waiter, `Yield`, lowering one's
  own priority, a new higher-priority thread). The program runs at 100,
  the shell's `spawnpri`. The kernel's ready and wait lists are kept on the
  host side; `kb_CurrentTask` in guest memory.
* **SPORT is from the SDK's documentation**, not from code: its copies
  happen at once, where the console waits for the vertical blank.
* The OS's structures are the SDK headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`):
  `clang -target armv4-none-eabi -c -Xclang -fdump-record-layouts` over
  them gives every field (Task and KernelBase this session), each checked
  against the 1993 code's stores or the game's reads; a folio's own node
  sizes come from its node database.
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`: 51 outputs), run from the submodule's commit and from the kit,
  compared byte for byte, when the kit's Python changes; the self-test;
  `pfcheck` (the six memory runs, `--memtest DIR --ops 4000 --seed 1..6`,
  and the eleven Graphics snapshots, calls 0, 8, 9, 11, 12, 14, 15, 17 to
  20); Immercenary's `p` and OMF2097's `LaunchMe` on `pfboot`. The battery
  script, OMF2097's extracted ISO and the other programs' `pfboot` build
  (`rop-build`, which reruns cmake itself when `runtime.cmake` changes)
  live in session scratchpads, outside the repositories: rebuild them if
  gone (`3dokit.disc --extract`; the battery's list is the one above). Commit in the kit,
  `git pull --ff-only` in the submodule, commit the port, record in
  `10-3dokit.md`.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* None open.

## Later, not next

* The audio folio's playback: native mixers for `mixer8x2`, `sampler`,
  `varmono8`, `dcsqxdhalfmono`, fed by the values the runtime keeps.
* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping:
  both could use `unwrap`, when a battery change is due anyway.
* The kernel's own lists (`kb_Devices`, `kb_TaskReadyQ` and the rest) are
  not filled by the runtime; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting items.
