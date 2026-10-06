# The oracle

What the port is compared with: the game running on something other than
the port. Two emulators were tried, and the user's console is the third
reference.

## The disc

The user's own pressing, which runs on their 3DO, was read from their
drive as 2048-byte sectors (`iso/disc-E.iso`, 307,351 sectors: the drive
returns all but the last 94 of the image's 307,446, all of them past the
volume's 307,200 blocks). Compared sector by sector with the image the
documentation pipeline measured: **0 of 307,351 differ**. Every file is
the same, `launchme`, `ex`, `Orion` and the scripts included. Whatever an
emulator does differently is the emulator's.

## How the disc starts (Phoenix, confirmed by the user)

1. `/ex` (= `/launchme`): an animated Crystal Dynamics logo, then **a
   choice between Crash 'n Burn and the Preview**.
2. Crash 'n Burn: an introductory movie, then the main menu: **Rally,
   Tournament, Options**.
3. Preview: `/Orion`, the *Total Eclipse* preview ("Coming Soon From
   Crystal Dynamics", "Space Combat at 24 Frames per Second"), which loops
   with the scripts (`runme1` runs `/ex`, `runme2` runs `/Orion`).

## The console (the user's 3DO, with the same disc)

The same as Phoenix (session 5, the user's look), with one difference: the
Crystal Dynamics logo animation goes **straight to the game's introductory
movie**, and the choice between Crash 'n Burn and the Preview never
appears. The choice is the game's own: `DoLogoScreen` (0x20ef0), one of
the screens `GlueShell`'s switch runs (0x1068), a dialog whose answer 1
starts `DoPreviews` and whose 0 or 0x7f goes on to the game. What makes
the console skip it is not known yet; it is something the game reads
(the pad, NVRAM, a timer, the hardware or OS it finds), since the disc and
the scripts are the same. The runtime will reach that screen and its
inputs by its own trace.

## Opera (libretro), in RetroArch: does not reach the game

`tools/oracle.py` drives it (screenshots on a timetable, buttons over the
network RetroPad, its own options, RetroAchievements off for the run). On
this disc it shows only the Preview, in a loop, from the first seconds:
neither the logo nor the choice appears, and no button leaves it (the
user pressed too). The same with `panafz10.bin` and with the original
FZ-1 `panafz1.bin`, and with each of the core's timing hacks (1, 3, 5, 6).
`opera_kprint` printed nothing to RetroArch's log or console. Read as:
`/ex` does not get as far as its first picture under Opera, and the
scripts fall through to `/Orion` every time -- not yet proved, since the
game's own prints would say and do not come out.

## Phoenix 2.8: runs the game

`D:\Tools\phoenix28\ph-win64` (outside the repositories), with the
English `translation.xml`; BIOS in `3DO\BIOS` (`panafz10.bin`,
`panafz1.bin`, from the retrobios archive), the disc in `3DO\CD-ROM` (a
hard link to `iso/disc-E.iso`). Its changelog names Crash 'n Burn three
times: "Crash'n'Burn working again" (1.9), and the pixel processor's
second-source order of operations and the palette fixed for it (2.3,
2.8). It is a GUI program, driven by the user. Its changelog speaks of
a debugger (breakpoints, trace, a device tree, debug dumps), but the 2.8
build exposes no debug option to the user (session 3, the user's look):
the game's `kprintf` output has no window there, and no trace of OS
calls comes out of it.

So: **Phoenix is the reference for pictures and sound, run by the
user**; the order of the game's OS calls and of its own messages comes
from the runtime's trace (`pfboot`) alone, checked against the game's
code. Opera is kept for automated runs of what it does run.
