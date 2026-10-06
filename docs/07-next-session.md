# Next session: the sound

Where things stand: the translator is whole (`09-recompiler.md`), and on
3dokit's Portfolio runtime `launchme` boots, prints `...cnb...`, opens the
Graphics folio, gets its memory from the OS's memory lists, makes its two
screens as the 1993 GRAPHIX makes them (checked by replaying each call on
the folio's own code), opens the SPORT device, clears both screens with it
(`03-executables.md`, "The screens" and "Devices and IO"), prints
`Initing Sounds and Music`, opens the audio folio and stops at the first
call not implemented: **audio -4 `LoadInsTemplate`**. Phase 4 of
`06-attack-plan.md` goes on into phase 6's first half: the audio folio's
calls, in the order the game makes them.

```sh
python -m 3dokit.recomp --out build/recomp launchme=build/disc/launchme --optest
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++
ninja -C build/recomp-build                 # with C:\msys64\mingw64\bin on the path
build/recomp-build/pfboot build/disc/launchme [--trace 2] [--lenient] [--max-calls N]
build/recomp-build/pfboot build/disc/launchme --snap N DIR      # the N-th OS call, before and after
python -m 3dokit.pfcheck build/disc/System/Kernel/os_code DIR... --graphix build/disc/System/Folios/GRAPHIX
python -m 3dokit.aif --decompress build/disc/System/Folios/AUDIOFOLIO audiofolio.bin
python -m 3dokit.aif --decompress build/disc/System/Kernel/os_code os_code.bin   # linked at 0x10000
```

## The calls, in the order the game makes them (`--lenient` preview)

1. Up to the SPORT device and the two clears -- done (calls 1 to 28).
2. `FindItem(MKNODEID(1, 4), "audio")`, `OpenItem`, `LookupItem`.
3. **`LoadInsTemplate`** (audio -4) of `system/audio/dsp/mixer8x2.dsp`,
   `varmono8.dsp`, `sampler.dsp`, `dcsqxdhalfmono.dsp` (0x2b8fc..0x2b930,
   the names at 0x2ba20..): where the run stops. The four instruments the
   game names (`03-executables.md`); the `.dsp` files are what `3dokit.dsp`
   already reads and verifies.
4. `AllocInstrument` (audio -8) of the mixer, then per voice
   `sprintf("LeftGain%d")` / `"RightGain%d"` through **Kernel -84
   `VFPRINTF`** (OMF2097's `LaunchMe` stops there too), `GrabKnob` (audio
   -16) and `TweakKnob` (SWI 0x40000) twice, and `AllocInstrument` of the
   voice: eight times; then `StartInstrument` (SWI 0x40001).
5. `CreateSizedItem(MKNODEID(4, 4), NULL)`: an audio item of type 4,
   `AUDIO_SAMPLE_NODE` by the 1.2 header -- to be checked against the
   1993 folio. The runtime's `CreateSizedItem` stops on it.

## The audio folio

* `System/Folios/AUDIOFOLIO` unpacks with its own decompressor (session
  4). Read it as GRAPHIX was read: its tags (node database, vectors, SWI
  table, `CREATEFOLIO_TAG_ITEM`), its start, then each call the game makes.
* The game reaches it by vectors (12 slots) and by SWIs (folio 4, 10 entry
  points: `03-executables.md`). Its items (templates, instruments, knobs,
  samples) are what the game holds; what it reads of them decides how much
  of their structure must be the folio's.
* `pfcheck --graphix` is GRAPHIX-only. The same replay on AUDIOFOLIO needs
  its glue table, its words checked, and the items it makes stood in for
  the runtime's way: worth generalising (a folio's description, not a
  second copy) when the audio calls start to be written.
* What it cannot do here: the DSP. The instruments are reimplemented by
  name as native mixers (`06-attack-plan.md`); for this phase it is enough
  that the items, knobs and their values are right, and nothing plays.

## Keep in mind

* **A Graphics call is checked by replaying it on GRAPHIX** (`pfboot --snap
  N DIR`, then `pfcheck ... --graphix`): eleven pass byte for byte (the
  folio's VDLs, `CreateScreenGroup`, `AddScreenGroup`, the averaging
  calls). A new Graphics call gets the same check. Its first run caught a
  wrong word in the runtime's VDLs.
* **SPORT is from the SDK's documentation**, not from code: its driver is in
  the console's ROM, not on the disc. Its copies and clones happen at once,
  where the console waits for the vertical blank: frame pacing will have to
  put them back at the VBL.
* **IOReqs, SendIO, CompleteIO** are the 1993 kernel's (`03-executables.md`,
  "Devices and IO"). A reply port, a callback, a named IOReq, an item's
  deletion, and any other device stop with "not yet".
* The OS's structures are the SDK headers' (`D:\Homebrew6\refs\3do-devkit\include\3dosdk`),
  offsets from `clang -target armv4-none-eabi -S` over them (1.2 and 1.3
  agree), each checked against the 1993 code's stores or the game's reads;
  the 1993 folio's own node sizes come from its node database (GRAPHIX's
  ScreenGroup and VDL are shorter than the headers').
* `--lenient` is a preview, not a run to trust.
* The oracle is Phoenix (`08-oracle.md`), for pictures and sound only.
* Every 3dokit change: the regression battery (`aif --scan` on the three
  trees, `dsp --verify`, and on the nine programs `portfolio --sites`,
  `arm60 --check`, `recomp.discover --report` and its function list, `arm
  --names`: 51 outputs), run from the submodule's commit and from the kit,
  compared byte for byte; the self-test; `pfcheck` (the six memory runs,
  and the Graphics replays); Immercenary's `p` and OMF2097's `LaunchMe` on
  `pfboot`. The battery script and OMF2097's extracted ISO live in a
  session scratchpad: rebuild them (`3dokit.disc --extract`). Commit in the
  kit, `git pull --ff-only` in the submodule, commit the port, record in
  `10-3dokit.md`. `pfboot` builds for the other programs need `cmake`
  again when the runtime gains a file.
* Python or C++ with backslashes in it goes through the Write or Edit
  tool, never a shell heredoc.

## Questions for the user

* On the console the start is Phoenix's, except that the logo goes straight
  to the intro movie, without the game/Preview choice (`08-oracle.md`).
  What decides it is the game's: the command line `main` reads, or the
  pad's answer to `DoLogoScreen` -- not the saves (`08-oracle.md`). The
  console is an FZ-10 that has played the game before.

## Later, not next

* The emitter's speed: flags only where read, literal pools folded.
* Ghidra's function list against discovery's (`--against`).
* `aif --scan` does not count `os_code` (its boot header), and `python -m
  3dokit.aif` on `os_code` or `misc_code` raises instead of unwrapping:
  both could use `unwrap`, when a battery change is due anyway.
* The kernel's own lists (`kb_Devices` and the rest) are not filled by the
  runtime's devices; nothing has read them yet.
* GRAPHIX's VDLTYPE_FULL and caller-made VDLs; deleting items.
