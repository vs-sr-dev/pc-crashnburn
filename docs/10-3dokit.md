# What this port gave 3dokit

3dokit (`3dokit/`, a submodule, from `D:/Homebrew6/3dokit` until it is
published) was started by Immercenary's port. Crash 'n Burn is its second
game, and the reason it became a repository of its own. Each entry is a
3dokit commit and what Crash 'n Burn asked of it.

| Session | 3dokit | What |
|---|---|---|
| 1 | f31ff76 | split out of pc-immercenary (its commit 76bf14d) with `git subtree split --prefix=3dokit`, from a clone, so that repository is untouched |
| 1 | 049c64e | the README's "Using it" for a submodule; `aif`: the relocation stub is where the BL at 0x04 points (Crash 'n Burn's three programs put it 4 bytes past `ro + rw`, and the word between is relocated: 3 failing of 34, then 0); `dsp`: the instrument format's version 1 (2 of the 53 in the 1993 set) |
| 1 | 370d4f7 | `arm`: the compiler's embedded function names (`Image.embedded_names`, `--names`): 292 on `launchme`, 47 on `Orion` |

Each change was checked on the kit's other two discs, Immercenary
(`PC-Immercenary/extracted`) and the OMF2097 port's ISO: `aif --scan` output
byte-identical before and after (57 and 39 images, 0 failing), `dsp
--verify` clean (64 and 77 instruments), no embedded names found on any
of their programs (so `arm`'s output is unchanged). pc-immercenary still
carries the kit in-tree at 76bf14d; moving it onto the submodule is that
port's step, when the user says.

## Session 2

| 3dokit | What |
|---|---|
| fa94852 | `aof` (the SDK's ARM Object Format libraries, and the folio glue in them), `sdk` (105 SWIs and 184 slots named from the 1.2/1.3/2.5 headers and the 3do-devkit's libraries), `portfolio` named from them and reading the 1993 SDK's folio opener and shared pool word: launchme 75 → 113 of 116 sites attributed |
| abdbb70 | `arm60`: the ARM60's instruction set, ARMv3 exactly, in pure Python; 0 disagreements with capstone on five programs |
| eb84fdc | `recomp.discover`: functions, code and data, switches, indirect transfers; 0 descents into data on five programs |

Checked on Immercenary's five programs and OMF2097's LaunchMe: `portfolio`
attributes the same slots to the same folios as before (only the names
change, to the SDK's); `arm60 --check` and `recomp.discover --report` run
clean on `p`, `p1e` and OMF2097's `LaunchMe`. The SDK also corrects one
reading in Immercenary's notes: SWI 0x10011 is `ReadHardwareRandomNumber`.

## Session 3

| 3dokit | What |
|---|---|
| 318214d | `armemu`: the ARM60 interpreter, the recompiler's reference (8 known-answer tests; 27,819 random instructions agree with unicorn's ARM926); `arm60`: MUL's should-be-zero Rn set is undefined |
| 87356c5 | `recomp.emit`, `python -m 3dokit.recomp`, `recomp.selftest`; the C++ runtime for recompiled code (`runtime/arm60.h`, `arm_core`, `arm_stub`, `arm_selftest`, `runtime.cmake`) |
| d15a333 | `recomp.discover`: a load of pc from the word a function parked its lr in is a return (Crash 'n Burn's 0x41fd8 and 0x42120); the self-test refuses writes to code words only |
| 627d87e | README: the other programs' self-test measured again |
| fce69b2 | `runtime/pf*`: Portfolio's frame (the boot, the OS's memory, folio tables of traps, SWI and slot dispatch by the SDK's names, the trace) and `pfboot`; `arm_swi` takes the swi's address |
| 5ffff74 | items (`FindItem`, `OpenItem`, `CloseItem`, `LookupItem`, the folios as items), `ChangeDirectory`, the OS's own allocations and untraced access |

Checked on Immercenary's six programs (`launchme`, `p`, `p1e`,
`SpeechSubroutine`, `CinepakSubroutine`, `StorageTuner`), OMF2097's
`LaunchMe` and Crash 'n Burn's `launchme` and `Orion`, before and after
the two commits that change what it runs, 318214d and d15a333 (`aif --scan` on the three trees, `dsp --verify`, `portfolio
--sites`, `arm60 --check`, `recomp.discover --report` and its function
list, `arm --names`): byte-identical, except `arm60 --check`'s count of
refused words (data that decoded as a `mul` with Rn set: 1 to 292 per
program) and `launchme`'s discovery report (pointer jumps 5 to 1). Every
function of the nine recompiles with nothing refused; the eight besides
`launchme` replay 1,016 functions, 15,722 vectors, with 0 failures.

After fce69b2 the instruction test, `launchme`'s 138 functions and the
eight other programs' 1,016 replay with 0 failures, and two of them boot
on `pfboot` too (Immercenary's `p` prints `GAME: Entering main game
task.`; OMF2097's `LaunchMe` reaches `AllocMemFromMemLists`). The other
commits touch no module the regression battery runs.
