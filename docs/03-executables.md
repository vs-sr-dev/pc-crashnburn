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
the zeros before it). Indirect transfers other than the OS's: 8 (session
3, `09-recompiler.md`) -- the drivers' AI table (`DoEnemyAi`, a tail jump
`ldr pc, [r1, r0, lsl #2]` through the table at 0x5cfb0),
`SpliceInOneObject`'s pointer call, one more pointer call at 0x37694, the
hand-written routine's `mov pc, r3` (the handler word before an object,
which the relocations show is the routine's own start), and four `ldr pc`
in two hand-written routines, 0x41fd8 and 0x42120, which are **returns**:
each stores its `lr` in a word of its own on entry (0x41fd4, 0x42118) and
leaves by loading `pc` from it. Session 2 read these as a table inline
after the call; it is not. Discovery now finds them as returns, which
leaves 4 transfers through pointers.

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

* **Screens**: `cnbOpenGraphics`, `InitHardware`, `AlterVDL`, `Bank 2
  (VRAM)`, `Bank 3 (VRAM)`: its own memory banks, two of them in VRAM, and
  VDLs it edits. (`Kernel VRAM` and `Task's VRAM` are lib3DO's
  `ReportMemoryUsage`, 0x2a8f8, which nothing calls.)
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

## Memory: what the game reads of the OS's

The game takes memory from the OS through the SDK's macros, and reads the
OS's memory structures itself, so they have to be where `mem.h` puts them:

* **Its banks** (`InitMemoryAllocationSystem`, 0x145c8):
  `AllocMemFromMemLists(KernelBase->kb_CurrentTask->t_FreeMemoryLists,
  ...)` (KernelBase +0x98, Task +0xa8) for bank 2, 0x64000 bytes of
  `MEMTYPE_VRAM|MEMTYPE_CEL` (`Bank 2: %d VRAM bytes.`), then bank 0,
  0xc0000 bytes of `MEMTYPE_DRAM|MEMTYPE_CEL` (`Bank 0: %d DRAM bytes.`),
  which the game then shares out itself (the messages of `SetImagePointers`
  and `AllocateMemory` name the banks).
* **Every frame** (`WriteMemoryUsageToRam`, 0x263c, from `TopOfFrame` and
  `GlueShell`): `mySumAvailMem` (0x2a898) over `kb_MemFreeLists`
  (KernelBase +0x74) and the task's lists, for DRAM and for VRAM: the first
  MemList whose `meml_Types & 0x70000` holds the kind asked (DRAM's
  `MEMTYPE_DRAM` masks to 0, so DRAM's MemList must come first), the sum of
  the `n_Size` of the free nodes on its `meml_l`, and the pages set in
  `meml_OwnBits` times its MemHdr's `memh_PageSize`; four words at
  0x56adc-0x56af8.
* **The screens' bank** (`cnbOpenGraphics`, 0x10f8): `GetMemType`
  (0x2e7f4, `FindMH` then `memh_Types`) of `GrafBase->gf_ZeroPage` (+0x78),
  masked to the bank bits (0x70000000), as `CSG_TAG_SPORTBITS`; a screen's
  size in pages from `gf_VRAMPageSize` (+0x80).

## The OS on the disc, read

`python -m 3dokit.aif --decompress` runs a compressed image's own
decompressor in the interpreter. The 1993 kernel, `os_code` v0.16, is an
AIF image behind a 16-byte boot header, linked at 0x10000, 49,968 bytes
unpacked, with no embedded names. What was read of it, and what the
runtime now does the same way (`3dokit/runtime/pf_mem.cpp`, checked
against these functions by `python -m 3dokit.pfcheck`):

* **Its tables**: the vector table ends at 0x1beac with slot -4 (`RemHead`);
  every slot read is where the SDK names it (-28 `AllocMemFromMemLists`
  0x15688, -32 `FreeMemToMemLists` 0x15370, -44 `ScavengeMem`, -52
  `memset`, -60 `GetPageSize`, -100 `FindMH` 0x15e4c, -104 to -116 the
  single-MemList functions). The SWI table runs backwards: SWI n at
  0x1bddc - 4n (0 `CreateSizedItem` 0x13228, 13 `AllocMemBlocks` 0x15d5c, 20
  `ControlMem` 0x16538, 33 `SystemScavengeMem` 0x157c0).
* **Slot -120** (0x10ea0), the one the startup calls and no header names,
  is the command line's parser: a non-zero word at the top of the stack is
  the command line the loader left there, split into `argv` below it;
  otherwise `argc` and `argv` go on as they came.
* **Memory**: a MemHdr per kind, DRAM (`MEMTYPE_DRAM|CEL|DMA`, priority
  101, 32 KB pages on a 2 MB machine) and VRAM (`BANKSELECT|BANK1|CEL|DMA|
  VRAM`, `BANK2` too above 1 MB, priority 100, 16 KB pages, 2 KB VRAM
  pages); a MemList per MemHdr on the OS's list and on every task's
  ("task dram ml" at the head, "task vram ml" at the tail). Allocations are
  16-byte multiples, first fit in address order from the bottom of a free
  node; pages for a task come from the bottom of the MemHdr, the OS's from
  the top; before asking for pages the allocator gives back every whole
  free page of the pool (`ScavengeMem`), and without `MEMTYPE_FILL` it
  writes the block's length into its first word.

`GRAPHIX` (built 16 August 1993) unpacks to 28,164 bytes. When it starts
it sets `gf_VRAMPageSize` to `GetPageSize(MEMTYPE_VRAM)` (2 KB), the
default display 320 x 240, a VBL of 16,684 us at 60 Hz, and takes two VRAM
pages from the OS's lists: the VIRS page and, after it, `gf_ZeroPage`.
Its user vector table ends at 0x542c (slot -4, `MapCel`); many of its
entries are two-instruction SWI glue. `CreateScreenGroup` (0x3e44) reads
its tags against those defaults, allocates the bitmaps' VRAM from the
caller's own lists (`MEMTYPE_VRAM|MEMTYPE_CEL`, page-rounded and
`MEMTYPE_STARTPAGE` with the SPORT bits) and hands the rest to SWI
0x20032.

## The screens, read in GRAPHIX

What `cnbOpenGraphics` (0x10f8) asks for and what the 1993 folio does
with it, read in `GRAPHIX` and now done the same way by the runtime
(`3dokit/runtime/pf_graphics.cpp`), each step checked by replaying it on
the folio's own code (`pfboot --snap`, `python -m 3dokit.pfcheck
--graphix`: every result and every byte of guest memory the folio's).

* **The folio's own node sizes** are in its node database (0x5430, the
  `CREATEFOLIO_TAG_NODEDATABASE` of its tags at 0x5444): ScreenGroup 0x54,
  Screen 0x7c, Bitmap 0x84, VDL 0x34 bytes. The 1993 ScreenGroup ends at
  `sg_Add_SG_Called` (no `sg_ScreenList`) and the VDL at `vdl_DataSize`;
  every field up to there is where the 1.2 header puts it.
* **Its system VDLs** (0x41b4, right after the VIRS and zero pages when
  the folio starts): two blocks of the OS's VRAM (`VRAM|DMA`, 0x180 and
  0xa0 bytes) hold forced-first, pre-display, post-display, a full entry
  over the VIRS page, and the blank VDL; the chain runs forced-first ->
  the full entry -> pre-display -> the blank VDL (or later the screens')
  -> post-display -> forced-first. `gf_VDLDisplayLink` (+0xb4) is the
  word of pre-display that points at what is shown. Each entry's header
  ends with 32 colour words, entry i being `i << 24` and the grey `i *
  255 / 31` (the blank VDL's are black). Forced-first is then written to
  the display hardware (0x3300580).
* **`CreateScreenGroup`, the user half** (0x3e44): tags 1 to 11 over the
  defaults (240 lines displayed and per screen, 2 screens, 1 bitmap,
  VDL type 4); checks (display height 1..240, screen height at least
  that, VDL pointers only with lengths, more than one bitmap only with
  heights); the array of buffer pointers from the caller's lists (flags
  0, DRAM) and each buffer `width * 2 * height` bytes of `VRAM|CEL`,
  page-rounded and `STARTPAGE|` the SPORT bits when there are any. The
  game's two buffers: 153,600 bytes each, 75 VRAM pages, bank bits
  0x50000000.
* **SWI 50, the supervisor half** (0x27a0): the group (`sg_ScreenHeight`,
  `sg_DisplayHeight`, `sg_Add_SG_Called` 0); it sets the bitmap count to
  1 whatever was asked. Per screen: the Screen item, its VDL (type 4,
  VDLTYPE_SIMPLE: one 38-word entry per bitmap from the OS's VRAM, a
  header of 240 lines, the bitmap's buffer twice, the link, a display
  control word chosen by the width -- 320, 384, 512, 640 or 1024 -- and
  the grey ramp; the last entry links to post-display; type 1, not read
  to the end, allocates `8 * height + 32` words a bitmap; types 2, 3 and
  5 are `GRAFERR_NOTYET`), the VDL item, `InitList(scr_BitmapList, "ScreenBitmapList")`, and its Bitmap:
  width, height, clip size, `bm_WatchDogCtr` 62,500, `bm_CEControl`
  0xe1500000, `REGCTL0` from an 18-entry table of widths (320 is 0x1414),
  `REGCTL1` the clip size, `REGCTL2`/`3` the buffer, the vertical offset.
  The bitmap goes into `scr_TempBitmap` and onto no list. The buffer must
  be writable by the task: the 1993 kernel's slot -168 (0x1617c, which
  the later headers call `IsMemReadable`) takes the task first and
  checks each page in its MemList's `meml_WriteBits`.
* **`AddScreenGroup`** (SWI 17) sets `sg_Add_SG_Called` once;
  **`Enable`/`DisableHAVG`** and **`VAVG`** (SWIs 5 to 8) set or clear
  bit 4 or 8 of the display control word of the screen VDL's first entry
  (both already set by the type-4 VDL). All of them first `CheckItem` the
  item (Kernel -64: `LookupItem`, then subsystem and type) and require
  the caller to own it.
* **Then the SPORT device**: lib3DO's opener (0x2d324) finds the device
  `SPORT` (`MKNODEID(1, 15)`), opens it, and creates two IOReqs for it
  (`CreateSizedItem(MKNODEID(1, 14), {CREATEIOREQ_TAG_DEVICE, device})`),
  kept at 0x6495c and 0x64960, the device at 0x64964. Without it
  `InitHardware` fails (`InitHardare failed`) and `main` tears down.

## Devices and IO, read in the 1993 kernel

What the game's SPORT calls need, read in `os_code` and done the same way
by the runtime (`3dokit/runtime/pf_io.cpp`):

* **The lib's IO glue** (1993's, linked in the game): `CheckIO`
  (0x2e728) is `LookupItem` then `io_Flags & IO_DONE` (+0x58); `WaitIO`
  (0x2e74c) returns at once when `IO_QUICK` is set, waits on the reply
  port when `io_MsgItem` is a message, and otherwise polls `CheckIO`
  around `WaitSignal(SIGF_IODONE)`; `DoIO` (0x2e7c4) sets `IO_QUICK` in
  the IOInfo, then `SendIO` and `WaitIO`. The game also polls `CheckIO`
  in loops of its own (`TopOfFrame` 0xc28, `DrawRoad` 0xedcc).
* **An IOReq** (`CreateSizedItem(MKNODEID(1, 14), tags)`, 0x13c88):
  tags `TAG_ITEM_NAME`, `TAG_ITEM_PRI`, `CREATEIOREQ_TAG_REPLYPORT` (10),
  `CREATEIOREQ_TAG_DEVICE` (11, required, and the device must be open);
  the node is `dev_IOReqSize` (0x70 by default) on the device's list
  "Device ioreqs", born with `IO_DONE|IO_QUICK`. Without a reply port,
  `io_MsgItem` and `io_SigItem` are both the task.
* **`SendIO`** (SWI 24, 0x142e8): the IOReq must be the task's and done;
  the 32-byte IOInfo is copied in; `ioi_Flags2` must be 0 and
  `ioi_Flags` only `IO_QUICK`; the unit at most `dev_MaxUnitNum`; what it
  receives into must be writable by the task (slot -168), what it sends
  from inside memory. The internal SendIO (0x142b4) clears `io_Error`,
  `io_Actual`, `IO_DONE`, sets `IO_QUICK` if asked, and jumps to the
  driver's dispatch.
* **`CompleteIO`** (0x141c0, a kernel function, no SWI in 1993):
  `IO_DONE`; a callback chains the next request; a quick request tells no
  one; otherwise a reply to the message, or `SIGF_IODONE` (8) to the task
  through the kernel's signal (0x19c70), which refuses bits outside
  `t_AllocatedSigs` (0xff from `CreateTask`, 0x16ce4).
* **The SPORT device is not on the disc.** Neither `os_code` (which names
  no device at all) nor `misc_code` (another kernel) nor any folio names
  it; the console's ROM brings it (the FZ-1 ROM's
  compressed programs open it, and none defines it). The runtime's SPORT
  follows the SDK's documentation ("The SPORT Device"): CLONE (4) and COPY
  (5) under the mask in `ioi_Offset`, FLASHWRITE (6) under
  `ioi_CmdOptions`, whole VRAM pages only. On the console a copy or clone
  waits for the vertical blank; here it is done at once.
* **What the game does with it** (0x1724): a 2 KB page of its clear
  colour (`InitClearPage` allocates 4 KB of `VRAM|CEL` and aligns down),
  CLONEd over the whole bitmap: 153,600 bytes from 0x200000 for the first
  screen. It clears both screens this way before `InitSoundsAndMusic`.

## The sound's set-up, read in AUDIOFOLIO

`InitSound` (0x2b8d4, from `InitSoundsAndMusic`) builds the game's whole
mixer before anything plays, and the runtime now makes every item of it
as the 1993 folio does (`3dokit/runtime/pf_audio.cpp`):

* **Four templates**: `LoadInsTemplate` of `mixer8x2`, `varmono8`,
  `sampler` and `dcsqxdhalfmono` (`system/audio/dsp/...`, from the
  current directory), kept at 0x64604, 0x64608, 0x6460c, 0x64614.
  `dcsqxdhalfmono` (SDX2-compressed sound) is not instanced here.
* **The mixer**: `AllocInstrument(mixer8x2, 0)`, priority 0, at 0x64610.
* **Eight voices**, 7 down to 0, each a 40-byte record from 0x6a294: the
  mixer's `LeftGain%d` and `RightGain%d` grabbed (`sprintf` into a stack
  buffer) and tweaked from a table at 0x64574 (two words a voice); then
  the voice's instrument at priority 100 -- `sampler` for 7 to 4,
  `varmono8` for 3 to 0 -- its `Frequency` and `Amplitude` knobs, and
  `ConnectInstruments(voice, "Output", mixer, "Input%d")`. The gains:
  voices 7 and 6 0x8c3 both sides, 5 right only, 4 left only, 3 to 0
  0x13d5, 0x2705, 0x14e5, 0x1445 both sides.
* `StartInstrument(mixer, NULL)`; then 59 empty samples
  (`CreateSizedItem(MKNODEID(4, 4), NULL)`, `AUDIO_SAMPLE_NODE`) into
  0x6a3d4; then `CreateThread("sound service", sound_service 0x2b7c4,
  stack 0x1000)` at the task's priority + 10 -- where the run stops.

What the folio does with them (V20.19, built 5 September 1993):

* **Its shape**: `CreateItem(MKNODEID(KERNELNODE, FOLIONODE))` at 0xc28
  with tags at 0xc070: node 0x348 bytes, 42 vectors (table 0xbfa4, slot -4
  last), 32 SWIs (table 0xbf24, SWI n at entry 31 - n: run backwards, as
  the kernel's), node type 4, a node database at 0xc04c (template 0x54,
  instrument 0x58, knob 0x34, sample 0x98, cue 0x38, envelope 0x74,
  attachment 0x54, tuning 0x34 bytes, all with `NODE_ITEMVALID |
  NODE_NAMEVALID`), and item routines (0x3c of the folio) whose
  `ir_Create` (0x1048) dispatches by node type.
* **Most calls first ask `ItemOpened(task, folio)`** (Kernel -128) and
  return `AF_ERR_AUDIOCLOSED` when the task has not opened the folio.
  `TweakKnob` and `ConnectInstruments` do not.
* **A template** is parsed in the caller's task (`iffParseFile`, with
  a form handler, 0x1854, for `3INS`, `DSPP`, `ATNV` and `ATSM`) and made
  by `CreateItem(..., {AF_TAG_TEMPLATE, the parsed DSPP})` (0x230c).
  **An instrument** (0x2104): `AF_TAG_TEMPLATE`, `AF_TAG_PRIORITY` (0 to
  255, default 100, the node's `n_Priority`), `AF_TAG_SET_FLAGS`; every
  knob is written its default raw (0x8cf0), and the instrument grabs its
  own `Frequency` and `Amplitude` if it has them, for `StartInstrument`'s
  tags. **A knob** (0x2684): `AF_TAG_NAME` (required, else
  `AF_ERR_BADNAME`) and `AF_TAG_INSTRUMENT`; the name is matched against
  the template's DKNB records with `strncmp` over 32 characters.
* **`TweakKnob`** (SWI 0, 0x27c8, and the tweak at 0x9780): the value
  through each target's calculation (0 as is, 1 `v*a+b`, 2 `v*a/b`, 3 `v
  / 44100`), the first result clamped to the knob's range, written to the
  DSP. `TweakRawKnob` (SWI 0x11) skips the calculation. Recorded in
  `3dokit/dsp.py`; every knob of the game's four instruments is type 0.
* **`ConnectInstruments`** (SWI 8, 0x8018): the source's variable by
  name, the destination's variable or else knob, and the destination's
  code relocated to read the source's: the DSP's own wiring.
* **The DSP is not reproduced.** The runtime keeps, per instrument, every
  value the folio would write to a knob resource, and its connections;
  `StartInstrument` records the start. Nothing plays: the instruments
  are to be native mixers by name (`06-attack-plan.md`).
* **No replay on the folio's code** as for GRAPHIX: the folio's items
  hold its own DSP bookkeeping (resource maps, code images, the DSP's
  memory), which is private (no SDK header) and which the game never
  reads -- it holds item numbers. The runtime keeps the ItemNodes as the
  folio's (sizes and flags from its node database) and the rest on the
  host side.

`sprintf` (the 1993 lib's, 0x2ead4) builds a FILE on the stack and calls
**Kernel -84 `vfprintf`** (os_code 0x1a184, Norcroft's printf core) with
its own `putc` (0x2f208) and a dummy floating-point printer (0x2f314): the
kernel formats and writes every character through the program's `putc`.
The runtime does the same, calling back into the recompiled code
(`pf_guest_call`).

## The sound thread, and tasks in the 1993 kernel

The last thing `InitSound` does is `CreateThread("sound service",
priority + 10, sound_service 0x2b7c4, 0x1000)` (the lib's 0x2ec94: the
stack from the task's own memory lists, then `CreateSizedItem(MKNODEID(1,
5))` with `TAG_ITEM_PRI`, `TAG_ITEM_NAME`, `CREATETASK_TAG_PC`,
`_STACKSIZE` and `_SP`). The thread opens the audio folio for itself,
allocates a signal (kept at 0x645f4), and loops: its priority up by 20
(0x2c2f8), `WaitSignal`, then for each of the eight voices with a request
queued at 0x645b4 -- `ReleaseInstrument`, `DetachSample`, `AttachSample` of
the sample the request names, `StartInstrument` with `AF_TAG_FREQUENCY`,
the voice's `Frequency` and `Amplitude` tweaked -- and its priority back
down (0x2c31c). So the game's sound effects reach the folio from this
thread, at a priority above the game's, woken by its signal.

What the kernel does (os_code v0.16), and the runtime now does the same
way (`3dokit/runtime/pf_task.cpp`):

* **The program's priority** is the shell's spawn priority: 100 (`spawnpri`
  in `System/Tasks/shell`, 0x64f0; it must stay between 10 and 200). The
  sound thread runs at 110, and at 130 while it waits.
* **CreateTask** (0x16a54): a thread is a task with `CREATETASK_TAG_SP`; a
  name is required; from a task that is not privileged the priority must be
  10 to 199; the stack at least 0x80 bytes. It shares its creator's memory
  lists (each of which the kernel gives a semaphore), starts with the
  eight system signals, `sl` at its stack's base + 0x80, `r0`/`r1` (and
  `r5`/`r6`) from `_ARGC`/`_ARGP`, `r9` (and `r7`) from `_BASE`, and returns
  to 0x168fc, which deletes it.
* **Signals**: `AllocSignal(0)` takes the highest free bit from bit 30 down
  (the thread's is 0x40000000); `WaitSignal` always waits for `SIGF_ABORT`
  too, and returns and clears the bits that came; `SendSignal` refuses the
  system's bits from a task that is not privileged.
* **The switch** (0x104fc, as any SWI returns): with
  `kb_PleaseReschedule` set and a task ready, the current task goes on if
  its priority is above the ready queue's head, else joins the queue behind
  its equals. A signal to a waiting task of higher priority, `Yield`, and a
  task lowering its own priority set the flag. CreateTask sets it only when
  the creator's priority is *above* the new task's, which changes nothing:
  a higher-priority thread waits for the next quantum tick. The runtime,
  without a timer yet, switches to it as the call returns.
* **The kernel's lists in guest memory** (`kb_TaskReadyQ`, `kb_TaskWaitQ`)
  are kept by the runtime on the host side; `kb_CurrentTask` is kept
  right, as the game reads it.

## Time: what the game asks of it, and what the 1993 OS does

What the game times, and how:

* **Its frame** waits for the vertical blank: `main` gets a timer IOReq
  (the lib's `GetVBLIOReq`, 0x2d710: the `timer` device opened, an IOReq
  made) into its globals (+0x29c), and `TopOfFrame` calls `WaitVBL(ior,
  1)` (0xd08; the lib's 0x2da30: `TIMERCMD_DELAY` on unit 0, `ioi_Offset`
  1, `SendIO`, `WaitIO`). Four more `WaitVBL` calls sit at 0x1f378,
  0x1f4dc, 0x2291c and 0x22a04.
* **Its sound** runs on the audio clock: `InitTimer` (0x2c254) takes the
  clock (`OwnAudioClock`) and keeps its owner and the old rate
  (`GetAudioRate`) at 0x64630, then sets 128 Hz (`SetAudioRate(owner,
  0x800000)`); `UninitTimer` (0x2c2ac) puts the rate back and lets the
  clock go. `GetAudioTime` (through 0x2c2ec) is read by `ChannelPlaying`,
  `PlayChannel`, `SetSemaphore` and `_MEDPlayer`; `SleepTask` (0x2d2f4,
  from `_MEDPlayer`) is `SleepUntilTime` on a cue kept at 0x64638, which
  `_MEDPlayer` makes as it starts (0x2bce0: `CreateSizedItem(MKNODEID(4,
  5), NULL)`, an `AUDIO_CUE_NODE`).
* `SetSemaphore`/`ClearSemaphore` (0x2c38c, 0x2c400) are the game's own:
  a byte counted up and down with its priority raised around it, and
  `Yield` while another holds it.
* The game reads none of the OS's clocks in memory.

What the OS does, read in its code (and, for the ROM's devices, in the
SDK's documentation):

* **The vertical blank**: GRAPHIX's FIRQ (0x50b4, "Graphics FIRQ",
  interrupt 1, priority 250) adds 1 to `gf_VBLNumber` (+0x74), setting
  bit 0 in an odd field (bit 11 of CLIO's 0x3400034), and writes the
  field's VDL into the display link. GRAPHIX's own wait (0x510c) spins
  until `gf_VBLNumber` changes.
* **The timer device** is not on the disc (the 1993 kernel names no
  `timer`; `misc_code` is a second build of the same kernel) but in the
  console ROM's Operator (below). Unit 0 counts vertical blanks, unit 1
  microseconds, five commands (table 0x25de0). `TIMERCMD_DELAY` (3,
  0x21694) on unit 0 always queues the request, `IO_QUICK` cleared, in
  order of `ioi_Offset`; at each blank (0x213a8) the timer's 64-bit count
  goes up by 1 and each queued request's `io_Actual` by 1, completing it
  once `io_Actual` reaches `ioi_Offset` -- a delay of n ends at the n-th
  blank after it is sent, of 0 at the next. `TIMERCMD_DELAYUNTIL` (4,
  0x217d4) first sets `ioi_Offset` to the count *less* `ioi_Offset` (the
  wrong way round: a time to come waits about 2^32 blanks) and is then a
  DELAY. `CMD_READ` (1) writes the count to an aligned 8-byte buffer;
  `CMD_WRITE` (0) is BADCOMMAND. The SDK's account ("The Timer Device")
  agrees for DELAY.
* **SPORT** (the Operator, 0x23188; commands 0 to 3 BADCOMMAND): copies and
  clones are queued (`IO_QUICK` cleared, 0x233ec) and done by the SPORT FIRQ
  at the vertical blank (0x22f80, on lines 10 to 13), `FLASHWRITE_CMD` at
  once (0x2337c). A command done at once returns 1, and the kernel's
  dispatch (os_code 0x1468c) then completes the request and `SendIO`
  returns 1.
* **Quick IO**: the lib's `DoIO` (0x2e7c4) sets `IO_QUICK` and its
  `WaitIO` (0x2e74c) returns at once while `io_Flags` has `IO_QUICK`. The
  kernel's `SendIO` clears `IO_DONE|IO_QUICK`, sets `IO_QUICK` back if
  asked, and jumps to the driver (0x142b4 to 0x142e4), whose result is
  `SendIO`'s; `CompleteIO` (0x141c0) tells no one while `IO_QUICK` is set.
  So a driver that queues a request clears `IO_QUICK` itself.
* **The audio clock** (AUDIOFOLIO): the DSP counts sample frames down
  from `head.dsp`'s `CountDown` knob and interrupts at 0; the folio's FIRQ
  ("AudioTimer", interrupt 11, 0x3e90) adds 1 to the time (folio +0x9c)
  and, when the earliest wake-up (+0xa0, flag +0xac) has come, signals the
  audio daemon, which runs its timer list (+0xb0; 0x460c: every node whose
  time is at or before now, unsigned, is taken off and its function called
  -- a cue's (0x4600) signals its owner). The folio's start (0x3f08) makes
  the semaphores "AFTimerListSem4" (+0xd0) and "AFTimerRateSem4" (+0xd8),
  the daemon (SWI 0xe, 0x4550) grabs `CountDown` (+0xd4) and sets 240 Hz.
  `OwnAudioClock` (-76, 0x448c) is `LockItem` of the rate semaphore without
  waiting: its item, else `AF_ERR_INUSE`; `DisownAudioClock` (-80) unlocks
  it. `SetAudioRate` (SWI 0xf, 0x43fc) turns a rate into a duration, `(DivUF16(44100.0,
  rate) + 0x8000) >> 16` -- 240 Hz is 184 frames, 128 Hz 345 -- and
  `SetAudioDuration` (SWI 0x10, 0x435c) wants the owner (else
  `AF_ERR_INUSE`) and 44 to 32,767 frames (else `AF_ERR_OUTOFRANGE`), then
  tweaks `CountDown` and keeps the duration (+0xe0). `GetAudioRate` (-60)
  is `DivUF16(44100.0, duration)`: 0x00EFAC85 at 184 frames;
  `GetAudioDuration` (-64) and `GetAudioTime` (-168) read the node.
  `DivUF16` is Operamath's (its slot -12, 0x2420; the folio's 0xb7c0
  reaches it through slot -16, `DivRemUF16`): `(n << 16) / d`, or
  0xFFFFFFFF when that does not fit or `d` is 0 -- 3,000 random cases run
  on its own code agree.
* **Semaphores** (os_code): made at 0x13960 (the waiters' list "Semaphore
  WaitQ" at +0x30, `sem_Owner` -1), `LockItem` (SWI 7, 0x13ad0 and
  0x139c8: `sem_bit` +0x24 swapped, `sem_NestCnt` +0x2c, a wait node on
  the kernel's stack with a signal of the task's own), `UnlockItem` (SWI 6,
  0x13b90 and 0x13b30: the owner only; at 0 the first waiter is signalled
  and owns it).
* **The kernel's quantum** is a FIRQ of its own ("kernel quanta", handler
  0x1780c, on a timer whose number KernelBase keeps): equal priorities take
  turns at its tick. Nothing in this game needs it yet.

How 3dokit's runtime does it (`3dokit/runtime/pf_time.cpp` and the
devices): the guest's clock is its own, moved on 1 us per safe point of
the recompiled code (an estimate of the ARM60's pace) and jumping ahead
when every task waits, so every run gives the same trace. The boot clears
its two screens in two fields (the SPORT copies now wait for the blank),
and `InitTimer` sets the audio clock to 345 frames a tick.

## The console ROM: what the disc does not bring

The File folio, the timer and SPORT are nowhere on the disc: not in
`System/Folios`, not in `os_code`, not in `misc_code` (a second build of the
same kernel: the same strings, "Could not find Operator process"). They are
in the console's ROM, which the user's Phoenix setup carries
(`D:\Tools\phoenix28\ph-win64\3DO\BIOS`, read locally only; nothing of it
goes in git). `python -m 3dokit.rom panafz1.bin` (the FZ-1's, 1993) lists:

* **An Opera volume** "rom" at 0x28000 whose block size is 4 bytes: `apps/`
  (AudioCD, ELDemo, InsertDisc, the Panasonic splash), `bin/` (the ROM's own
  audiofolio, graphix, operamath, eventbroker, chknvram, format), `audio/`.
* **Fifteen AIF images**, twelve compressed, each unpacked by its own
  decompressor. Ahead of the volume: the boot's kernel (0x20a0, linked at
  0x10000), the **Operator** (0xa830, linked at 0x20000, "Operator Version
  ..., BuildDate: Tue Aug 3 17:06:15 PDT 1993": the timer, xbus, SPORT,
  MKE CD-ROM and File devices, the idle task, `/bin/shell`) and the **File
  folio** (0x188a0, linked at 0: filesystems, open files, the program
  loader's "Can't allocate program area").
* **The File folio's tables**: 10 vectors at 0x6584 (slot -4
  `OpenDiskStream` 0x4e40, -8 `ReadDiskStream` 0x5110, -12
  `SeekDiskStream` 0x55f4, -16 `CloseDiskStream` 0x5094; -20 to -40 0x6084,
  0x5ac0, 0x5668, 0x5868, 0x587c, 0x5a58), 14 SWIs at 0x654c (0x23b4,
  0x3938, 0x3684, 0x378c, 0x3620, 0x3598, 0x3514, 0x3f08, 0x33d8, 0x2370,
  0xc84, 0x394c, 0x349c, 0x3388 in table order; the numbers run backwards,
  as the kernel's and the audio folio's do: SWI 0 is the last word),
  `CREATEFOLIO_TAG_DATASIZE` 0x10c.

## The File folio, read in the ROM

The FZ-1 ROM's File folio (`0188a0_000000.bin` from `3dokit.rom --unpack`,
linked at 0, no embedded names), as far as the game reaches it, done the
same way by the runtime (`3dokit/runtime/pf_file.cpp`):

* **The SWIs** run backwards from 0x654c: 0 `OpenDiskFile` 0x3388, 1
  `CloseDiskFile` 0x349c, 4 `MountFileSystem` 0x2370, 5
  `OpenDiskFileInDir` 0x33d8, 7 `ChangeDirectory` 0x3514, 8
  `GetDirectory` 0x3598, 9 `CreateFile` 0x3620, 10 `DeleteFile` 0x378c, 11
  `CreateAlias` 0x3684. The folio reaches the kernel through stubs that
  name its internal functions (0x5e8 `CreateItem` 0, 0x5f8 `DeleteItem` 3,
  0x608 `OpenItem` 5, 0x620 `CloseItem` 8, 0x6a0 `CompleteIO` -8) and the
  kernel's vectors (0x16c `AllocMemFromMemLists`, 0x184 `FreeMem...`,
  0x1b4 `LookupItem`, 0x6110 `memcpy`).
* **A task's file data** (0x82c, made the first time a task needs it):
  its current directory (the folio's root at first), its program
  directory, its last error, its list of aliases.
* **The path walker** (0x2614): a `/` (leading, or doubled) goes to the
  folio's root; `.` stays, `..` goes to the parent, `^` to the root of the
  current filesystem; a name of 32 characters or more is BADNAME
  (0xD556F104); any other name is looked up first in the folio's list of
  known files and then on the medium, NOTADIRECTORY (0xD556F102) when the
  place reached is not a directory, NOFILE (0xD556F101) when nothing has
  that name. A name that starts with `$` is an alias (0x23b8: the current
  task's list, then its owner's, up the chain, names compared without
  case by the kernel's `FindNamedNode`): the path is built again with the
  alias's value in place of the name, and the walk goes on from there.
  `{a|b}` alternatives exist and are not met yet.
* **Aliases come from the shell.** No string `boot` or `exdir` is in the
  ROM. The disc's own shell (`System/Tasks/shell`, compressed) runs `alias
  boot /` followed by a name the kernel keeps (KernelBase + 0x110, compared
  with `rom` first), `cd $boot`, then `^/system/scripts/startopera`; that
  script makes `audio`, `drivers`, `c`, `s` and `app`, starts the event
  broker and the folios, and runs `^/AppStartup`, which makes `exdir`
  (`$boot`) and runs `runme1`. The game's task is the shell's child, so its
  `$exdir/CNB/...` finds the shell's alias. The ROM's own startup script
  (in its volume) makes `top`, `audiocd`, `eldemo` and the rest for the
  ROM's applications.
* **`OpenDiskFile`** (0x3388): the walk, then 0x24d8: an OpenFile device
  (`CreateItem` with the folio's driver, the File's name, priority 1,
  FileIOReqs of 0x8c bytes; 0x98 bytes; made while the task is briefly
  privileged, so the task owns it), `ofi_DeviceType` 2, `ofi_File`, the
  File's use count up, opened (`OpenItem`). `CloseDiskFile` (0x349c):
  an OpenFile of this driver, else BADITEM (0xD556F001); `CloseItem`,
  `DeleteItem` -- whose device hook (0x2438) gives the File one use less.
* **The driver** (`CREATEDRIVER` tags at 0x6694: dispatch 0xd9c, abort
  0xd88, init 0xcb0, 11 commands). The dispatch is the folio's own, and
  `SendIO` returns what it returns: a command above 10 is BADCOMMAND
  (0xD556F00C) and the request is left as it was. `CMD_STATUS` (0x107c) is
  answered at once: a FileStatus (driver 5, family 3, size 0x28, the
  File's block size and count, its flags, `DS_USAGE_READONLY` for a
  read-only file, `fs_ByteCount`) copied to the receive buffer -- 0x28
  bytes when the buffer is shorter, the folio having written a max for a
  min --, `io_Actual` untouched, `CompleteIO`, and 0. Everything else but
  `FILECMD_GETPATH` goes to the filesystem's queue; a CD's (0x117c, an
  OptimizedDisk's, set at 0x1e60) takes only `CMD_READ`, of whole blocks
  (else 0xD556F009), clears `IO_QUICK` and queues the request: `SendIO`
  returns 0 and the read finishes later, `io_Actual` growing by what the
  drive moved (0x17c0), whole blocks. A refusal is `io_Error`,
  `CompleteIO` and the error back.
* **The streams** (vectors -4 to -16) are user-mode code over those calls.
  `OpenDiskStream` (0x4e40): the Stream (0x38 bytes, `MEMTYPE_FILL`, from
  the task's lists), `OpenDiskFile`, an IOReq, `DoIO` of `CMD_STATUS`
  into its stack, a buffer (`-bSize` blocks, at most the file's; `bSize`
  rounded up to whole blocks; by default 2 blocks, 1 for a file of two
  blocks or fewer; at least 256 bytes; `MEMTYPE_DMA`), and the first read
  sent and left running -- so `OpenDiskStream` fails if `SendIO` is not 0:
  a read must never be done at once. `ReadDiskStream` (0x5110) takes the
  running read in (waiting for it only when a seek is pending), makes a
  pending seek inside the buffer or starts again from the seek's block,
  copies out what the buffer holds up to the end of the file, reads what
  is still wanted straight into the caller's buffer in whole blocks and a
  last part block through its own, and sends for the next blocks while
  the buffer has room. `SeekDiskStream` (0x55f4) only records where the
  next read starts (`SEEK_END` counts back from the end: length less
  offset). `CloseDiskStream` (0x5094) waits for a running read and undoes
  the rest. The folio has its own `CheckIO`, `WaitIO` and `DoIO`
  (0x6230, 0x6254, 0x62cc), the same as the 1993 library's.
* **What a file's last block holds**: past the file's end, the disc has the
  eight letters `iamaduck` over and over, by the byte's place in its block
  -- every file that ends inside a block, on this disc (414 of 415) and on
  OMF2097's (1,495 of 1,497), but `rom_tags` and OMF2097's `BannerScreen`.
  A stream's buffer holds those bytes after its last read; the runtime's
  reads give them too.

What the game does with it:

* **`LoadSFX`** (0x2ab64), for each of the 14 names at 0x64338:
  `OpenDiskStream(name, 0)`; `SeekDiskStream(0, SEEK_CUR)`, `(0,
  SEEK_END)` for the length, back with `SEEK_SET`; `ReadDiskStream` of the
  length plus 4 into the 0x48000-byte sound area allocated in
  `InitSFXandMusic`; `CloseDiskStream`; then 0x2b214 sets one of the 59
  empty samples to the data: `SetAudioItemInfo` with the tags 0x16 (1 for
  8 bits, else 2), 0x31 (8), 0x17 (1), 0x18 (the length, halved when not 8
  bits), 0x19 (0x3c), 0x2e (0x2000 << 16), 0x1f and 0x20 (-1 and -1; for
  `engine1` and `flamer`, 12 and 13, 0 and the length: a loop over the
  whole sound), 0x24 (the address) and 0x23 (the length); on an error the
  sample is deleted. What each tag is, is the audio folio's to say.
* **`InitHardware`** then reads `$exdir/CNB/Glue/Chars.bin` and `Plate.3do`
  (0x2d3c4, unnamed library code past `SleepTask`, through the streams), and
  `CDIO_OpenAFile` (0x3070) opens `$boot/bigfile` and makes eight IOReqs on
  it, whose reads the game polls with `LookupItem` until done.
