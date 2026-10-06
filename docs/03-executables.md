# The executables

The disc, its file system, its formats and its curiosities are measured in
the documentation pipeline,
[3do-crashnburn-doc](https://github.com/vs-sr-dev/3do-crashnburn-doc): one
data track, the Opera file system, 451 files, and the boot chain. This
port reads the same disc with 3dokit (`python -m 3dokit.disc`: 451 files,
38 directories, every copy compared) and starts where that work stopped
being useful to a port: the code.

## The boot chain, briefly

`/AppStartup` runs `runme1`, which runs `/ex` and then `runme2`, which runs
`/Orion` and then `runme1` again: a circle between the game and the
`blazer` preview. `/ex` and `/launchme` are byte-identical. The port's
target is `/launchme`; `/Orion` is a second, optional one.

The OS is on the disc: `/System/Kernel/os_code`, v0.16 by its ROM tag (the
1993 Portfolio, older than Immercenary's 23.10), and three folios, two of
them compressed (`AUDIOFOLIO`, `GRAPHIX`), and `OPERAMATH`.

## AIF

| | `/launchme` | `/Orion` |
|---|---|---|
| file | 433,928 | 178,380 |
| read-only (code and constants) | 0x444e4 = 279,780 | 0x1bf10 = 114,448 |
| read-write | 0x20c5c = 134,236 | 0xdd08 = 56,584 |
| zero-init | 0x5650 = 22,096 | 0x26ec = 9,964 |
| entry | 0x100 | 0x100 |
| relocations | 4,930 | 1,789 |
| 3DO binary header at 0x80 | none (1993) | none |
| functions (`3dokit.arm`) | 584 | 156 |
| named by the compiler | 292 | 47 |

The relocation stub is 4 bytes past `ro + rw` on both (and on `/ex`), and
the word between is part of the image: one of Orion's relocations points
at it. 3dokit's `aif` took the BL at 0x04 as the authority for this
(`10-3dokit.md`).

## The code

* **Compiler**: Norcroft ARM C, APCS with frame pointers (`mov ip, sp`
  then `stmfd sp!, {..., fp, ip, lr, pc}`), and **embedded function
  names**: each of the game's functions is preceded by its name and a word
  `0xff000000 + length`. `python -m 3dokit.arm build/disc/launchme --names`
  lists them. The game's code is 0x644 (`main`) to 0x2d2f4 (`SleepTask`);
  the libraries linked after it are unnamed.
* **Indirect jumps** in reached code, all of them:

  | kind | count | |
  |---|---|---|
  | folio vector, `ldr pc, [rN, #-slot]` | 116 | the OS boundary |
  | return, `mov pc, lr` | 114 | (plus `ldm ..., pc`) |
  | switch, `addls pc, pc, rN, lsl #2` + `b` table | 16 (17 in session 1: one was data the linear sweep reached; `recomp.discover` finds 16) | `GlueShell`, `FMV_DecompressFrame`, `DrawHUD`... |
  | through a pointer in the data, `ldr pc, [...]` | 15 | `StartCars`, `PlayerSpecialCheck`, `DrawBitmapCar`, `SpliceInOneObject`... |

* **Function pointers**: 47 relocated words point at function starts, 45
  distinct functions: 28 words in tables in the data, 19 in literal pools
  (an address loaded to be stored or handed on). The tables hold `InitializePlayerCar`/`MovePlayerCar`/
  `InitializeEnemyCar`/`MoveEnemyCar`; the seven drivers' `...DriveCode`
  (Fang, Druger, TasmanTwix, MaxAmillion, Klaw, Rocker, Drone); the
  weapons' `...Init`/`...Move`/`...Launch`; `CarDeathInit`/`Animate`/
  `Flames`.
* **Call graph** (`3dokit.arm --stats`): 584 functions, 477 called by
  `bl`, 19 only by a tail `b`, 88 by neither; 432 reached from the entry
  by calls. The 88 are the pointer tables' targets, callbacks handed to
  the OS, and dead code; to be sorted in phase 3.
* **No hardware access**: no ROM, MADAM or CLIO address is loaded or
  built by reached code. Everything goes through Portfolio.
* **The startup** (0x100, the AIF entry): the OS hands over the arguments
  in r5 and r6 and **KernelBase in r7**; the startup keeps it in `sb` and in
  a global (0x56730), calls Kernel slot -120 (a runtime initialisation no
  SDK header names), and branches to `main` with the OS's `lr` (so `main`
  returning returns to the OS; `swi 0x11` at 0x128 is the exit after it).
  Every compiled function checks its stack (`cmp sp, sl; bllt 0x13c`), and
  0x13c jumps to Kernel slot -124, the kernel's stack extension: a runtime
  with a large stack and a low `sl` never takes it.

## The OS surface (`python -m 3dokit.portfolio build/disc/launchme --sites`)

Every number below is named by the SDK (`3dokit.sdk`: the 1.2, 1.3 and 2.5
SDKs' headers, which agree, and the 3do-devkit's libraries' glue). Names
are the SDK's; what each does in this game is phase 4's to check.

**SWIs**: 274 sites, 34 entry points (the 35th, `swi 0` x11, is data the
linear sweep decodes as `svcne #0`):

| folio | | |
|---|---|---|
| 0 | 1 | `0x11` exit (the AIF header's own, at the startup's end) |
| 1 Kernel | 17 | CreateSizedItem x17, DeleteItem x17, OpenItem x8, CloseItem, FindItem x2, SetItemPri x2, WaitSignal x5, SendSignal, AllocSignal, Yield x3, SendMsg x2, GetMsg x2, ReplyMsg, SendIO x7, ControlMem x4, SetFunction (in `main`), kprintf x122 |
| 3 File | 5 | OpenDiskFile x9, CloseDiskFile x8, ChangeDirectory, CreateFile, DeleteFile |
| 4 audio | 10 | TweakKnob x21, StartInstrument x3, ReleaseInstrument x2, StopInstrument, ConnectInstruments x3, DisconnectInstruments x3, SetAudioRate x2, LinkAttachments x2, SetAudioItemInfo, TestHack x2 |
| 5 Operamath | 1 | MulManyVec3Mat33_F16 x6 |

**Items opened by name**: the devices `SPORT` (twice), `mac` (twice),
`timer`; the folios `Graphics`, `audio`, `File`.

**Folio vectors**: 116 sites, 113 slots, every one attributed to its folio
and all but one named:

* **Graphics, 38**: the screens (CreateScreenGroup, AddScreenGroup,
  RemoveScreenGroup, DisplayScreen, SetVDL, SubmitVDL, the CLUT's
  SetScreenColor(s)/ResetScreenColors, Enable/Disable H/VAVG), the cel
  engine (DrawCels, DrawScreenCels, SetCEControl, SetCEWatchDog, MapCel),
  the bitmap's clip and read address, and the 2D pen calls (MoveTo, DrawTo,
  FillRect, WritePixel, ReadPixel, GetPixelAddress, DrawChar, DrawText8/16,
  the font CCB);
* **Kernel, 29**: lists (AddHead/Tail, RemHead/Tail, RemNode, InsertNode*,
  InitList, FindNamedNode), memory (AllocMem/FreeMem from mem lists,
  ScavengeMem, GetPageSize), items (LookupItem, CheckItem, IsItemOpened),
  memset/memcpy, USecToTicks/TicksToTimeVal, GetSysErr, vfprintf,
  WaitPort -- and slot -120, which the AIF startup calls at 0x80 and no
  SDK header or library names;
* **audio, 42**: instruments and templates (LoadInstrument, AllocInstrument,
  LoadInsTemplate, DefineInsTemplate, UnloadInstrument...), samples
  (LoadSample, MakeSample, AttachSample, ScanSample...), knobs (GrabKnob,
  GetNumKnobs, GetKnobName), envelopes, tunings, delay lines, the clock
  (GetAudioTime, SleepAudioTicks, SleepUntilTime, Own/DisownAudioClock);
* **File, 4**: OpenDiskStream, ReadDiskStream, SeekDiskStream,
  CloseDiskStream.

A slot named is a slot the game's library glue *can* reach. **What the
game's code really reaches** (`3dokit.recomp.discover`: only code that
control flow reaches from the entry, the names, the prologues and the
relocated pointers) is much less, and it is the HLE's whole job:

| | reached | |
|---|---|---|
| SWIs | 33 | exit, CreateSizedItem, DeleteItem, FindItem, OpenItem, CloseItem, SetItemPri, WaitSignal, SendSignal, AllocSignal, Yield, SendMsg, GetMsg, ReplyMsg, SendIO, ControlMem, SetFunction, kprintf; OpenDiskFile, CloseDiskFile, ChangeDirectory, CreateFile, DeleteFile; TweakKnob, StartInstrument, ReleaseInstrument, StopInstrument, ConnectInstruments, DisconnectInstruments, SetAudioRate, LinkAttachments, SetAudioItemInfo; MulManyVec3Mat33_F16 |
| Graphics | 14 | DrawCels, MapCel, CreateScreenGroup, AddScreenGroup, DisplayScreen, SetScreenColor(s), Enable/DisableHAVG, Enable/DisableVAVG, SetClipOrigin/Width/Height |
| Kernel | 11 | AllocMemFromMemLists, FreeMemToMemLists, FindMH, LookupItem, IsItemOpened, memset, memcpy, vfprintf, GetSysErr, WaitPort, and slot -120 (the startup's) |
| audio | 12 | LoadInsTemplate, UnloadInsTemplate, AllocInstrument, GrabKnob, AttachSample, DetachSample, GetAudioRate, GetAudioTime, SleepUntilTime, Own/DisownAudioClock, ControlAudioDevice |
| File | 4 | Open/Read/Seek/CloseDiskStream |

No `DrawScreenCels`, no VDL calls (the strings' `AlterVDL` is the game's
own, on its screen's colours), no 2D pen calls: every picture is a cel.

## Discovery (`python -m 3dokit.recomp.discover build/disc/launchme --report`)

553 functions (292 named, 46 more by prologue, 214 more as call targets,
the entry), 43,793 code words; everything else in the image is data. 16
switches (one whose last case's code follows the table). 17 functions are
never called, tail-called or pointed at -- dead code: `SFXOn`/`SFXOff`,
`MusicOn`/`MusicOff`, `ShootScreen`, `ReportMemoryUsage`, `CheckOverlap`,
`ConcatenateAll`... Hand-written code sits past the compiler's read-only
area, at 0x445d8, inside the read-write data (it saves every register into
the zeros before it). Indirect transfers other than the OS's: 8 -- the
drivers' AI table (`DoEnemyAi`, `ldr pc, [r1, r0, lsl #2]`),
`SpliceInOneObject`'s pointer call, two library routines that load `pc`
from `[lr]` (a table inline after their call, 0x41fd8 and 0x42120), the
hand-written routine's `mov pc, r3`, and one more pointer call at 0x37694.

**Library functions**: 28 of the 292 unnamed functions match a
3do-devkit library function word for word over their whole length
(relocated words and branch offsets masked): the kernel stubs at 0x304 to
0x454, `__rt_sdiv`, `__rt_udiv`, `__rt_sdiv10`, `FindNamedItem`, `strcpy`,
`rand`, `atoi`, the `*DiskStream` and `AddScreenGroup` glue. The rest
differ: the devkit's libraries are later builds than 1993's.

**DSP instruments** (`python -m 3dokit.dsp build/disc/System/Audio/dsp --used
build/disc/launchme`): 4 of the 53 on the disc, `varmono8`, `mixer8x2`,
`sampler`, `dcsqxdhalfmono`.

## What the strings say the game does with the OS

* **Screens**: `cnbOpenGraphics`, `InitHardware`, `AlterVDL`, `Kernel
  VRAM`, `Task's VRAM`, `Bank 2 (VRAM)`, `Bank 3 (VRAM)`: its own memory
  banks, two of them in VRAM, and VDLs it edits.
* **Files**: its own CD layer, `CDIO_OpenFileSystem`, `CDIO_OpenAFile`,
  `CDIO_ReadSectors` (whole sectors only), `CDIO_Seek`, `CDIO_ASYNCRead`
  (`SendIO`, a pool of IOReqs), on which `ASYNC_LoadSomeMore` streams the
  track while racing. Saves: `/nvram/CNBSIXTHCIRCUIT`, `/nvram/CNBTESTSAVE`
  through `CreateFile`, `OpenDiskFile`, `DoIO`.
* **Sound**: `InitSFXandMusic`, `LoadTrackMusic`, `_MEDPlayer`,
  `_GetMODData`, `FindPeriod` (an Amiga period table: the module player
  is the game's), `LoadInstrument`, `AttachSample`, a `Knob` grabbed,
  `mixer8x2.dsp` by path.
* **Movies**: `FMV_Open`, `FMV_DecompressFrame`, `FMV's CCB buffer`: the
  studio's codec, drawn as a cel.
