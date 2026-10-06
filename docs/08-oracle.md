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
2.8). It is a GUI program, driven by the user; it has a debugger
(breakpoints, trace, a device tree, debug dumps) and knows the SWIs by
name, which is where the game's `kprintf` output is to be looked for.

So for now: **Phoenix is the reference for pictures and sound, run by the
user**; Opera is kept for automated runs of what it does run.
