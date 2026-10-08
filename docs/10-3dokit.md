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

## Session 4

| 3dokit | What |
|---|---|
| b7eed62 | `aif`: compressed images unpacked by their own decompressor, run in `armemu` (`decompress`, `--decompress`); `os_code`'s 16-byte boot header (`unwrap`) |
| 93c2c33 | `runtime/pf_mem`: the MemHdrs, the OS's and the task's MemLists and the allocator, as the 1993 kernel runs them; `pf_graphics`: the Graphics folio's node; list primitives; `pf_boot`; `pfboot --memtest` and `pfcheck`, which replays the run on the kernel's own code |

Checked with the battery on the nine programs and the three trees (`aif
--scan`, `dsp --verify`, `portfolio --sites`, `arm60 --check`,
`recomp.discover --report` and its function list, `arm --names`), run from
the submodule's 5ffff74 and from the new kit: all 51 outputs
byte-identical. `launchme`'s self-test (the instruction test and three
vector sets: 1,275 functions, 18,393 vectors) replays with 0 failures; the
runtime change touches only the Portfolio objects, which the self-test
does not link. On `pfboot`, Immercenary's `p` runs to its 19th OS call
(`memset`) and OMF2097's `LaunchMe` to its 2nd (`VFPRINTF`).
`pfcheck`: six runs of 4,000 memory calls, every result and every byte of
guest memory the kernel's; two faults put in by hand are caught.

| 3dokit | What |
|---|---|
| 5723f89 | Kernel `memset` and `memcpy` (a memmove, as the 1993 kernel's) |

Checked the same way (battery from 93c2c33 and from the kit: 51 outputs
byte-identical; self-test 0 failures); Immercenary's `p` runs to its 20th
call (`SendIO`), `launchme` still stops at `CreateScreenGroup`.

## Session 5

| 3dokit | What |
|---|---|
| 332b0f1 | `runtime/pf_graphics`: the folio's system VDLs and its screen groups (`CreateScreenGroup`, `AddScreenGroup`, `Enable`/`DisableHAVG`/`VAVG`) as the 1993 GRAPHIX makes them; the kernel's `CheckItem` and its write check; `pfboot --snap` and `pfcheck --graphix`, which replays one Graphics call on the folio's own code; `aif.relocated` |

Checked with the battery on the nine programs and the three trees, run
from the submodule's 5723f89 and from the new kit: all 51 outputs
byte-identical. The self-test (1,275 functions, 18,393 vectors) replays
with 0 failures; `pfcheck`'s six runs of 4,000 memory calls from the new
boot are clean; Immercenary's `p` and OMF2097's `LaunchMe` stop where
they did (their 20th and 2nd calls), with the same traces. The new check
on the folio's own code: its start of the system VDLs and `launchme`'s
ten Graphics calls up to `SPORT` agree with the runtime byte for byte
(its first run caught a wrong constant in the runtime's full VDL entry),
and two faults put in by hand are caught.

| 3dokit | What |
|---|---|
| 3fccf88 | `runtime/pf_io`: devices, IOReqs, `SendIO` and `CompleteIO` as the 1993 kernel runs them, the task's allocated signals, a device's open count; the SPORT device from the SDK's documentation |
| 70c0567 | README: the same |

These touch no module the regression battery runs (the battery's Python
is 332b0f1's). The self-test replays with 0 failures; `pfcheck`'s six
memory runs and the eleven Graphics replays from the new boot are clean.
On `pfboot`, Immercenary's `p` now runs to its 113th call (`DeleteItem`:
the `timer` device it asks for at its 18th does not exist yet, and it
sends 47 IOReqs that were never made); OMF2097's `LaunchMe` still stops
at its 2nd (`VFPRINTF`).

## Session 6

| 3dokit | What |
|---|---|
| ef39953 | `dsp`: a knob record's targets (resource, calculation type, two operands), as the 1993 audio folio reads and applies them; `--verify` checks each record is its targets long and writes knob resources |
| 7e6feec | `runtime/pf_audio`: the audio folio's templates, instruments, knobs and samples as AUDIOFOLIO V20.19 makes and checks them (`LoadInsTemplate`, `AllocInstrument`, `GrabKnob`, `TweakKnob`, `TweakRawKnob`, `StartInstrument`, `ConnectInstruments`, an empty sample), without the DSP; `CreateSizedItem` to a folio's own creation routine; the kernel's `vfprintf` through the program's `putc` (`pf_guest_call`) and `ItemOpened`; the disc as a host directory, names matched without case (`pfboot --disc`) |
| c46c7e7 | README: the same |

Checked with the battery on the nine programs and the three trees, run
from the submodule's 70c0567 and from the new kit: all 51 outputs
byte-identical (`dsp --verify`'s new checks pass on all 651 knobs). The
self-test replays with 0 failures; the six memory runs and the eleven
Graphics snapshots from the new boot are byte-identical to session 5's,
which `pfcheck` passed. Immercenary's `p` runs to its 113th call with the
same trace; OMF2097's `LaunchMe` now prints `3DO-OMF2097 Battle MVP
starting` through `vfprintf` and its own `putc` and stops at its 36th
call (`FindAndOpenItem`, SWI 0x24, not yet). `launchme` makes its whole
mixer and stops at its 211th call, creating its sound thread.

| 3dokit | What |
|---|---|
| 596251b | `runtime/pf_task`: threads (`CreateSizedItem` of a task with `CREATETASK_TAG_SP`), `AllocSignal`, `FreeSignal`, `WaitSignal`, `SendSignal`, `Yield`, `SetItemPri` on a task, and the kernel's switch as an OS call returns, as os_code v0.16 runs them; a host thread per task, one running at a time; the program's task at the shell's spawn priority |
| 9de0fc4 | README: the same |

The battery's Python is c46c7e7's (unchanged). The self-test replays with
0 failures. The boot now writes the program's task's priority and ready
flag, so the six memory runs and the eleven Graphics snapshots differ
from session 5's in those two bytes; `pfcheck` passes all seventeen (0
results and 0 bytes differ). Immercenary's `p` and OMF2097's `LaunchMe`
give the same traces as with 7e6feec. `launchme` starts its sound thread,
which waits for its signal, and stops at its 218th call,
`OwnAudioClock`.

## Session 7

| 3dokit | What |
|---|---|
| 5587c75 | `runtime/pf_time` and the devices: the guest's clock (a fixed amount per safe point, a jump to the next event when every task waits), the vertical blank (GRAPHIX's `gf_VBLNumber`, SPORT's copies at the blank, the timer device's vertical-blank unit), a queued request clearing `IO_QUICK`, the audio clock as AUDIOFOLIO V20.19 keeps it (`OwnAudioClock`, `DisownAudioClock`, `Get`/`SetAudioRate`, `Get`/`SetAudioDuration`, `GetAudioTime`, Operamath's `DivUF16`), semaphores (`LockItem`, `UnlockItem`) as os_code makes them; README |

No Python changed, so the battery's outputs are c46c7e7's. The self-test
replays with 0 failures; the six memory runs and the eleven Graphics
snapshots from the new boot pass `pfcheck` (0 results and 0 bytes differ;
the boot now makes three more items -- the audio clock's two semaphores and
the timer device -- so item numbers and the OS's addresses move up).
OMF2097's `LaunchMe` makes the same 36 calls. Immercenary's `p` now finds
the timer and waits out 47 vertical blanks (0.78 s) before stopping at its
351st call (`DeleteItem`, not yet). `launchme` clears its screens at the
first two blanks, sets its audio clock and stops at its 234th call, the
File folio's `OpenDiskStream`.

| 3dokit | What |
|---|---|
| 2653b42 | `rom`: a console ROM's Opera volume (blocks of 4 bytes) and its AIF images, unpacked by their own decompressors; the runtime's SPORT and timer drivers as the FZ-1 ROM's Operator runs them (a command done at once returns 1, the kernel's dispatch completes it and `SendIO` returns 1; the timer's DELAY always queued and counted in `io_Actual`, DELAYUNTIL's subtraction, `CMD_READ`); README |

The battery from the submodule's 5587c75 and from the new kit: all 51
outputs byte-identical (the new module touches none of the others). The
three programs' traces are 5587c75's: `launchme` stops at its 234th call,
`p` at its 351st, `LaunchMe` at its 36th.

## Session 8

| 3dokit | What |
|---|---|
| f9058a0 | `runtime/pf_file`: the File folio as the FZ-1 ROM's image does it -- paths walked as its 0x2614 walks them, aliases of a task and its owners (the shell's from the disc's own scripts, `CreateAlias`), `OpenDiskFile`/`CloseDiskFile` (an OpenFile device with the folio's driver: `CMD_STATUS` at once, `CMD_READ` of whole blocks queued and done at the next safe point, the mastering's `iamaduck` fill past a file's end), `ChangeDirectory` giving the directory's File item, the four stream functions step for step; `pf_io`: the kernel's `DeleteItem` for IOReqs and devices (a device's delete hook), a driver refusing with an Err, `CreateIOReq` and `SendIO` for the OS's own code; `pf_kernel`: `OpenItem`/`CloseItem` for the OS, item numbers freed; README |

No Python changed, so the battery's outputs are c46c7e7's. The self-test
replays with 0 failures; the six memory runs and the eleven Graphics
snapshots from the new boot pass `pfcheck` (0 results and 0 bytes differ;
`ChangeDirectory` now makes the root's File node, 0x5c bytes more than the
old stand-in, so the OS's addresses move up). OMF2097's `LaunchMe` makes
the same 36 calls. Immercenary's `p` now deletes its timer's IOReq (its
351st call) and stops at its 352nd (`DetachSample`, not yet). `launchme`
reads its fourteen sound effects and stops at its 240th call, the audio
folio's `SetAudioItemInfo`.

| 3dokit | What |
|---|---|
| 67e7693 | the `iamaduck` fill: a comment, after the earlier disc surveys (Alone in the Dark has none) |

## Session 9

| 3dokit | What |
|---|---|
| b068375 | `runtime/pf_audio`: `SetAudioItemInfo` on a sample as AUDIOFOLIO V20.19 does it (its tags, frames and bytes, loops' bounds; the base frequency from the folio's default tuning and Operamath's `MulUF16`, checked on its own code), a new sample at the folio's defaults; README |

No Python changed. The self-test replays with 0 failures, the six memory
runs and the eleven Graphics snapshots pass `pfcheck`, and the three
programs' traces up to `launchme`'s 234th call, `p`'s and `LaunchMe`'s
whole runs are byte-identical to 67e7693's. `launchme` takes its fourteen
samples and stops at its 403rd call, GRAPHIX's `SetScreenColor`.

| 3dokit | What |
|---|---|
| c985e36 | `runtime/pf_graphics`: `SetScreenColor`, `SetScreenColors`, `ResetScreenColors`, `DisplayScreen` as GRAPHIX does them, the blank linking the field's VDL in; `pfboot --frames DIR` (what the VDLs show, a PPM per change); a stop inside an OS call names the call's site, not `lr`; README |

The traces up to `launchme`'s 234th call and `p`'s and `LaunchMe`'s whole
runs are 67e7693's but for the stop's last line, which now names the
call's own site (`p` 0x26918 for 0x2691c, `LaunchMe` 0x15474 for 0x16988 --
its `lr` there was a register of its own). Self-test 0 failures; the six
memory runs and the eleven Graphics snapshots pass, and five new ones
(calls 615, 616, 634, 2090, 2093) replay byte for byte on GRAPHIX.
`launchme` runs to its 2,262nd call, the audio folio's
`DisconnectInstruments`.

| 3dokit | What |
|---|---|
| 6ad2ac7 | `runtime`: a folio's `ir_Delete` behind the kernel's `DeleteItem` (`pf_on_delete`), the kernel's vector 34; the audio folio's knobs and instruments deleted (an instrument's knobs with it), `DisconnectInstruments`, a sample made with tags; README |

The three traces are c985e36's, byte for byte (the 59 empty samples print
nothing new); self-test 0 failures; the six memory runs and the sixteen
Graphics snapshots pass. `launchme` runs to its 2,289th call, the audio
folio's `AttachSample`.

| 3dokit | What |
|---|---|
| 5b96bc2 | `runtime/pf_audio`: attachments (`AttachSample`, `DetachSample`, an instrument's with it), `LinkAttachments`; README |

`launchme`'s trace to its 234th call and `LaunchMe`'s are byte-identical;
`p` now gets two calls further (`DetachSample(0)` is the kernel's
BADITEM, then `UnloadSample`, not yet). Self-test 0 failures; six memory
runs and sixteen Graphics snapshots pass. `launchme` plays its first
movie to its end and stops at its 14,822nd call, `StopInstrument`.

| 3dokit | What |
|---|---|
| f29a0a6 | `runtime/pf_audio`: `StopInstrument`, the instruments' and attachments' states as AUDIOFOLIO keeps them (`StartInstrument` starting each FIFO's first attachment without `NOAUTOSTART`), deleting a playing attachment, a sample |
| 5c29642 | `runtime/pf_os`: `--snap` also before a call not implemented yet |
| 94a5707 | `runtime/pf_cel` (new): the cel engine; `DrawCels` as GRAPHIX starts it (Graphics -172, SWI 39) |
| 8072d33 | README |

Only the runtime's C++ changed (no battery). The three traces (`launchme`
to its 234th call, `p`, `LaunchMe`) are session 9's byte for byte;
self-test 0 failures over 1,029 functions; the six memory runs and the
sixteen Graphics snapshots pass. `launchme` ends its movie and draws its
choice dialog for ever (no pad: no event broker).

| 3dokit | What |
|---|---|
| 1083701 | `runtime/pf_msg` (new): MsgPort and Message items, `SendMsg`, `ReplyMsg`, `GetMsg`, `GetThisMsg`, their deletion, as os_code v0.16; ports of the OS's own. `runtime/pf_event` (new): the event broker at its message boundary, the Control Pad's frames. `pfboot --pad` |
| 87b1d60 | README |

Only the runtime's C++ changed (no battery). `LaunchMe`'s trace is
byte-identical. `launchme`'s to its 234th call differs only by the item
numbers (one more: the broker's port, made at the boot) and the OS's
memory addresses after it (the port's 0x50 bytes and name). `p` now finds
the broker, configures itself as an observer, and stops at the File
folio's `GetDirectory` (before: "unable to open the event broker", then
its timer). Self-test 0 failures over 1,029 functions; the six memory runs
pass; the sixteen Graphics snapshots pass, the five after the 229th call
renumbered by the input library's eleven new calls (615, 616, 634, 2090,
2093 are now 626, 627, 645, 2101, 2104). With `--pad a@1300x1`
`launchme` plays its intro movie and reaches the Select Game menu.

| 3dokit | What |
|---|---|
| 2e68c83 | `runtime/pf_cel`: an `LRFORM` cel (a bitmap's line pairs), PRE0's BGND bit with the CCB's. `runtime/pf_audio`: cues and the folio's timer list (`SignalAtTime`, `SleepUntilTime`, `GetCueSignal`, a cue deleted). `runtime/pf_math` (new): Operamath's `MulManyVec3Mat33_F16` as MADAM's matrix engine computes it. README |

Only the runtime's C++ changed (no battery). The three traces
(`launchme` to its 234th call, `p`, `LaunchMe`) are session 11's byte for
byte; self-test 0 failures over 1,029 functions; the six memory runs and
the sixteen Graphics snapshots pass. With seven presses `launchme` goes
through Select Character, the circuit, its champion's movie and the
pre-race screen, loads the race (22 seeds on the recompiler's command
line, `09-recompiler.md`) and stops at its first stretched cel.

| 3dokit | What |
|---|---|
| 1c6cb66 | `runtime/pf_cel`: the projector as 3DO's patent WO 94/10644 describes it (stretched, turned, bent cels; ACW/ACCW), the origin's V and H bits, USEAV and PXOR in the pixel processor. `runtime/pf_audio`: `ReleaseInstrument`. `runtime/pf_graphics`: `SetClipOrigin`, `SetClipWidth`, `SetClipHeight`. `runtime/pf_os`, `pf_kernel`: a deleted item's node and name given back to the OS's memory. README |

Only the runtime's C++ changed (no battery). The three traces are session
11's byte for byte; self-test 0 failures; the six memory runs and the
sixteen Graphics snapshots pass; the 2,687 fields `launchme` shows up to
the Select Circuit screen are those of 2e68c83 byte for byte (the
projector on square cels, the OS's memory used again). The race runs:
before the OS's memory was given back it filled at field 53,850.

| 3dokit | What |
|---|---|
| f1af788 | `runtime/pf_task`, `pf_kernel`, `pf_io`: DeleteItem of a task as os_code's 0x167cc does it (its items deleted as by it, its opened items closed, its semaphores unlocked, `SIGF_DEADTASK` to its owner). `runtime/pf_audio`: `UnloadInsTemplate` and a template's deletion. `runtime/pf_kernel`: `SetFunction` refused to a task without privilege. `runtime/pf_main`, `pf_graphics`: `pfboot --pad BUTTONS@FIELD[xN][/E][+H]` (a press held H fields) and `--frames-at FIRST[-LAST][/EVERY]`. README |

Only the runtime's C++ changed (no battery). The three traces are session
12's byte for byte; self-test 0 failures; the six memory runs and the
sixteen Graphics snapshots pass; the 2,687 fields to the Select Circuit
screen are 1c6cb66's byte for byte. With A held `launchme` drives three
laps, shows its Rankout screen, and, told QUIT, ends.

| 3dokit | What |
|---|---|
| b7fe71b | `runtime/pf_window` (new, with SDL3): `pfboot --window` -- the display in a window in real time, the keyboard and a gamepad as the pad -- and `--record FILE` (the presses as `--pad` options). `runtime/pf_event`: the pad from the host, the record. `runtime/pf_graphics`, `pf_time`: the field for the window, the wait without limit in real time. `runtime.cmake`: the window joined to pfboot when SDL3 is found (statically linked). README |

Only the runtime's C++ and cmake changed (no battery). The three traces
are session 12's byte for byte; self-test 0 failures; the six memory runs
and the sixteen Graphics snapshots pass; the 2,687 fields to Select
Circuit are f1af788's byte for byte.

| 3dokit | What |
|---|---|
| efdcd36 | `runtime/pf_window`, `pf_event`: the record in LF lines and written at any exit; Esc no longer ends the window's run (the user's window closed mid-race, most likely on Esc). |

The same checks as b7fe71b, all byte for byte.

| 3dokit | What |
|---|---|
| ca71e86 | `recomp/emit`: the clocks the ARM60 takes (`clocks`: the ARM6 datasheet's S, N and I cycles, an N cycle two clocks, a failed condition one), paid at the start of each block (`ARM_TICK`), a conditional instruction's rest inside its `if`, a multiply's internal cycles from rs at run time (`arm_mul_m`). `runtime/arm60.h`, `pf.h`, `pf_time`: the budget in clocks, `ARM_POLL` a check only, the guest clock moved on 80 ns a clock (12.5 MHz; `g_pf_clock_ns`, `PF_POLL_EVERY` 1024 clocks) instead of 1 us a safe point. README |

The kit's Python changed: the battery's 51 files are efdcd36's byte for
byte (the emitter's output is not in it). Self-test 0 failures; the six
memory runs pass; the sixteen Graphics snapshots pass with the late ones
renumbered 624 625 643 2101 2102 (two fewer steps of a fade before them).
The traces of Immercenary's `p` and OMF2097's `LaunchMe` are session 12's
byte for byte; `launchme`'s to its 234th call differs in one line, the
time its first wait begins (0.000822 s, was 0.000520). By design the
fields no longer match the last build's: the pictures up to Select Circuit
are the same in the same order (2,200 against 2,205: one transition, after
the press on Select Character, in 2 steps instead of 7), at fields a
little later.

| 3dokit | What |
|---|---|
| 62c582d | `runtime/pf_graphics`: Graphics -4 `MapCel` as GRAPHIX's 0x14f4 does it, with GRAPHIX's own division (0x424, `__rt_sdiv` unrolled: bits 30 to 0, d = 0 gives 0x7FFFFFFF with n's sign); the display's picture from the pre-display entry on, so the system's VIRS line is no longer its first line (240 lines, not 241). |

Only the runtime's C++ changed (no battery). Self-test 0 failures; the six
memory runs and the sixteen Graphics snapshots pass; the three traces are
session 14's (`tr14`) byte for byte; the 2,764 frames to the race's start
are ca71e86's byte for byte without its first line. `MapCel`: six calls
from the user's play replayed on GRAPHIX (`pfcheck`, 0 bytes differ); the
division against GRAPHIX's run in armemu on 20,256 pairs, edge cases
among them, 0 differ.

| 3dokit | What |
|---|---|
| afb58de | `runtime/pf_cel`: PIXC MS 10 and 11, the multiplier from the decoded pixel's own colour (its component's top three bits + 1; MS 10's divider from the low two), as Opera's PPROC reads them -- the guide's PIXC section has the bits the other way round. |

Only the runtime's C++ changed (no battery). Self-test 0 failures; six
memory runs and sixteen Graphics snapshots pass; the three traces are
`tr14` byte for byte; the 2,764 frames to the race's start are 62c582d's
byte for byte (the mode stopped the run before, so nothing earlier used it).

| 3dokit | What |
|---|---|
| ac527c2 | `runtime/pf_file`, `pf_main`: `pfboot DISC --boot` -- the shell carrying out the disc's scripts from `startopera` on (aliases; `bg`, `bgkill`, `killkprintf`, `minmem` passed over; the OS's own programs under /System left to the runtime; every other program run to its end; scripts naming each other for ever), then `$boot/LaunchMe`; the File folio's streams for the OS's own code. `pf_time`, `pf_graphics`, `pf_io`: the clock, GRAPHIX's field count and the timer's going on from one program's boot to the next. `pf_audio`: `LoadInstrument` (0x14ec), `LoadSample` (0x2884, the folio's IFF reader and AIFF handlers), `AF_TAG_SAMPLE` (0x3b00), `UnloadSample` (0x3c78). `pf_cel`: TWD. `recomp.discover`: `add`/`sub lr, pc, #k` before a pc write is a call; `local_returns` (hand-written local subroutines), which `recomp.emit`'s returns go back to. README |

The kit's Python changed: the battery's 51 files are afb58de's but one,
Orion's discovery report (55 more words of code; two pointer jumps now
calls). Self-test 0 failures; the six memory runs and the sixteen Graphics
snapshots pass; the three traces are `tr14` byte for byte; the 2,764
frames to the race's start and 2,997 race frames (fields 8000-14,000) are
afb58de's byte for byte; `launchme` keeps its 46,350 instructions. Orion
(three seeds) runs to its `exit(0)`; through the shell, the user's QUIT
play goes on to the preview and back to the game's logo.

| 3dokit | What |
|---|---|
| c6a174b | `runtime/pf_dsp` (new): the DSP -- `mixer8x2`, `mixer4x2`, `sampler` (with `oscupdownfp`), `varmono8`, `dcsqxdhalfmono` transliterated from their code, known by its checksum (FNV-1a of DCOD), run a frame at a time in the folio's priority order into the mixers' bus; the DSP's arithmetic as FreeDO reads it, a 20-bit ALU; the FIFOs' DMA (current and next chunks, the interrupt). `pf_audio`: the DMA programmed as AUDIOFOLIO does it (start 0x74b8, release 0x79a0, stop 0x7cf8, links 0x7860/0x7810/0x7788, the daemon 0x5cc0/0x5c04, `LinkAttachments` while playing); the sound made in the guest's time at each folio call and audio tick. `pf_main`: `--wav FILE`. `pf_window`: the sound through an SDL3 audio stream. `dsp.py`: the instruction set and the relocation chains documented, `--dis`. README (FreeDO credited) |

The kit's Python changed: the battery's 51 files are ac527c2's byte for
byte (`--dis` is new; `--verify` unchanged). Self-test 0 failures; the six
memory runs and the sixteen Graphics snapshots pass; the three traces are
`tr14` byte for byte; the 3,207 frames of the run to the race's start
(`--max-calls 100000`, now reaching field 8792) and the 2,997 race frames
(fields 8000-14,000) are ac527c2's byte for byte. The SDX2 path against
`3dokit.audio`'s decoder: 401,092 values, 0 differ. The user heard the
game's sound (menus, music, effects, movies) right.

| 3dokit | What |
|---|---|
| 680b8d9 .. ea1b2e5 | PC-Immercenary's session 22 (the pipeline pivot onto this kit): `recomp.emit` -- every pc-derived address is the module's base (`mb`) plus the address linked at 0, so a program runs wherever it is loaded and several are loaded at once (`arm_load`, `arm_lookup` by address); `recomp.discover` -- the AIF header's relocation stub and zero-init as functions of their own extents, and a local return reached only through lr followed inside the function. The runtime: 23.10's File folio loaders (`LoadCode`, `ExecuteAsSubroutine`, `UnloadCode`), `GetDirectory`, the 1994 shell's `@`/`%`/`fg`, IOReqs with a reply port, `WaitPort`, semaphores made and deleted, the kernel's list vectors and `exit`, `ReadHardwareRandomNumber` (CLIO's RandSample a fixed xorshift32), `QueryGraphics`, audio `MakeSample`/`ScanSample`/`GetAudioItemInfo`/`UnloadInstrument` and the attachment calls (`MonitorAttachment`'s cue), 23.10's `dcsqxdhalfstereo`, gated `dcsqxdhalfmono`, `envelope` and `mixer2x2` in `pf_dsp`, PRE0's LITERAL bit passed over. The kit's own README and commits carry the detail |
| 5d008e9 | PC-Immercenary's session 23: 23.10's `fixedmonosample` and `directout` in `pf_dsp`, for its main menu's music. Runtime only, no emitter change: this game's traces, frames and sound the same byte for byte |
| c0614cd .. 5ff9786 | PC-Immercenary's session 23: LoadProgram and tasks with their own image, a task's end, AbortIO, Operamath's vectors and 4x4 engine, the Graphics folio's deletions -- and **the drive's reading time** (150 blocks of 2048 bytes a second, one read after another, no seek). Runtime only. This game's traces (`tr14`'s) and self-test are the same, but its timing is not: loading now takes the console's time, so the frames from field ~3 on differ and `frames.sh`'s pad script lands at other moments (the race is still reached and plays); the pfcheck snapshots 624, 625 and 643 are other calls now (13 still at Graphics calls, 0 bytes differ). The baselines (`cnb-old`'s frames, the snapshot numbers, the playtest pads) want re-recording on this kit. The user saw the Total Eclipse preview run faster than on the console (08): the drive's time is the first place to look again |

Checked at every one of those kit commits, against this game: its C++ is
the old C++ with `(mb + ...)` around the pc-derived constants and nothing
else (discovery adds no function to `launchme` or `Orion` that changes
what runs); the three traces are `tr14`'s byte for byte; the 3,207 frames to
the race's start and the 2,997 race frames are c6a174b's byte for byte; the
sound over `--max-calls 100000` is c6a174b's byte for byte (the disc carries
`mixer2x2`, `envelope` and `dcsqxdhalfstereo` with the same code as
Immercenary's, unused there); pfcheck's six memory runs and sixteen
Graphics snapshots pass; self-test 0 failures; the battery differs only by
discovery's two AIF routines per program and their report line. The
submodule moved here with `build/recomp` regenerated (the ArmModule
descriptor changed): `launchme` 577 functions, `Orion` 138.

| 3dokit | What |
|---|---|
| aeb5a62 | PC-Immercenary's session 24: `runtime/pf_dsp` -- an interpreter of the DSP's instruction set (FreeDO's reading), which runs any instrument with no hand-written model from its own code (Immercenary's spires), with its relocations, imported subroutines and ring registers placed as the folio places them; `pfboot --dsp-code` (every instrument from its code) and `--dsp-check` (each model's frame against its code). `pf_audio`: the template carries DRLC, `LoadInsTemplate` loads the subroutines an instrument imports, 23.10's knob calculation 4. README |

Runtime only, and the kit's Python only in a docstring: the battery's 51
files are 5ff9786's byte for byte. This game's four models (its 1993
`dcsqxdhalfmono`, `mixer8x2`, `sampler` with `oscupdownfp`, `varmono8`)
against the interpreter over two plays (`play-pad-pause`, `play-pad-2`,
3,000,000 calls each; 1.7 billion instrument frames): 0 differ; the sound
of both plays is 5ff9786's byte for byte. Self-test 0 failures; the six
memory runs pass; the three traces are 5ff9786's (and session 22's)
byte for byte; the 1,131 frames to field 3216 and the 2,974 race frames
are 5ff9786's byte for byte.

**The baselines re-recorded on the drive's time** (5ff9786 is the
reference now, the first with it): pfcheck's late snapshots 624, 625 and
643 are calls 1092, 1093 and 1111 now -- the same `SetScreenColor` and
two `DisplayScreen`, 468 calls later -- and all sixteen pass (0 bytes
differ); `frames.sh`'s two runs give 1,131 and 2,974 frames.

| 3dokit | What |
|---|---|
| eb96a85 | README only: this port among the ports built on the kit, now that it is published; the recompiler and the runtime named in the opening |

## pc-doctorhauzer's session 1 (the third game, Portfolio 20.21)

| 3dokit | What |
|---|---|
| 81c0e85 | `aif`: an image with a NOP at 0x04 has no relocation list -- this disc's kernel (`os_code`, at 0x10000) had found one only by chance; its unpacked bytes are unchanged |
| 9a38b90 | runtime: each folio's own version (`pf_system_version`) decides `CreateScreenGroup`'s buffer table and the Graphics and audio folios' node sizes; this disc's GRAPHIX 20.31 and AUDIOFOLIO 20.19 keep 1993's way |

Nothing here moves: the battery's 51 files, the self-test, the six memory
runs and sixteen Graphics snapshots, the three traces, a `--boot` run of
60,000 calls and the 1,131 and 2,974 frames are eb96a85's byte for byte.

## pc-doctorhauzer's session 2

| 3dokit | What |
|---|---|
| 1f46573 | runtime: the System images' decompressor in C++ (`pf_aif`, `pfboot FILE --unpack OUT`: 27 of the three discs' 28 compressed images as armemu unpacks them, this disc's `GRAPHIX`, `AUDIOFOLIO`, `os_code`, `misc_code`, `eventbroker` and `shell` among them); GRAPHIX laid in the OS's memory with its built-in font, for 20.45 only (`pf_font`: on this disc's 20.31 nothing is laid; the OS's allocations stop below 0x4E0000); `pfcheck` on GRAPHIX 20.45 (the 1993 path unchanged) |

Nothing here moves: the self-test, the six memory runs and sixteen
Graphics snapshots (with the old and the new `pfcheck`), the trace to call
234, a `--boot` run of 60,000 calls and the 1,131 and 2,974 frames are
9a38b90's byte for byte.

| 3dokit | What |
|---|---|
| aceddb7 | runtime: Kernel -88 `GetSysErr` as the 20.21 kernel does it, its tables and the File folio's error texts read from the disc's own `os_code` (`pf_err`); another kernel stops (this disc's programs do not call it) |

Nothing here moves: the same checks as 1f46573's, byte for byte.

| 3dokit | What |
|---|---|
| 0903c17 | runtime: the Operator's `ram` device and the NVRAM behind its unit 3 (`pf_nvram`, `pfboot --nvram DIR`); the File folio 20.30's linked-memory filesystem (mount, `CreateFile`, `DeleteFile`, `DismountFileSystem`); a signed, privileged program's task; the shell running `System/Programs`' programs when the build has their modules (pc-doctorhauzer's session 3, its `docs/05`) |

**A new baseline for the traces**: the `ram` device is one more item, made
at the boot, so every later item's number is one greater and the OS's
later allocations 0x70 bytes higher. Nothing else moves: built without the
device, the trace to call 234 (529 lines) and the `--boot` run of 60,000
calls (124,396 lines) are aceddb7's byte for byte; with it they differ only
in item numbers and OS addresses (0 lines otherwise). The self-test, the
six memory runs and sixteen Graphics snapshots, and the 1,131 and 2,974
frames are unchanged. This disc's 1993 File folio (20.19) keeps its own
`CMD_STATUS` (0x28 bytes copied); its NVRAM is blank, nothing is mounted.
