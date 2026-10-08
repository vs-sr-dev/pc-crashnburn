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

An FZ-10 that has played the game before. **The same start as Phoenix**
(session 5, the user's look): the logo animation, then the choice between
Crash 'n Burn and the Preview, then the intro movie and the menu.

Holding A or Start during the logo animation skips the choice: the game
goes straight to the intro movie. The choice is the game's own dialog,
`DoLogoScreen` (0x20ef0, screen 28 of `GlueShell`'s switch), read from the
pad (`DialogInput`, 0x1f148, with `GetJoystick`'s bits); a button down as
it comes up confirms its first entry, Crash 'n Burn (answer 0 or 0x7f: the
game; 1: `DoPreviews`). Without a button, the console waits on the choice
as Phoenix does.

Two other ways round it, read in the code, not seen: `main` (0x75c) shows
the choice only when the word at 0x56768 is -1, as it is in the image, and
sets it from the command line (0x670): one argument of one or two digits
below 30 skips the choice and hands the number on (0x79c). The saves play
no part there (`LoadGameCheck`, NVRAM's `CNBTESTSAVE`, is reached only from
`DoHackTitleScreen`, later).

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

## The first picture, beside Phoenix's (session 9)

Three Phoenix screenshots (`panafz10`, 953 x 686 JPEG, in
`D:/Tools/phoenix28/ph-win64/3DO`, outside the repositories): two of the
logo movie's last frame, and one of the choice that follows -- the same
frame with the two buttons, **CRASH'N BURN** (lit) and **PREVIEWS**, drawn
over its lower part.

The runtime's last field of the movie (`pfboot --frames`, VBL 1194, the
VIRS line dropped) set beside the first two: the logo's bounding box
gives a scale of 3.000 x 2.876 and puts the whole 320 x 240 field at
(-2, -1) in Phoenix's picture -- less than one source pixel off, so
Phoenix shows the 240 lines and 320 pixels with no crop. The logo's
purple averages (149, 4, 196) in Phoenix and (153, 0, 201) here, within
what the JPEG explains; the stars and the lettering fall in the same
places. The movie's picture, the CLUT and the line pairs are right as far
as one frame shows; the display control words (interpolation) are still
not modelled.

## The choice screen, beside Phoenix's (session 10)

The runtime's dialog field (`pfboot --frames`, VBL 1197, once both
buffers hold the buttons) set beside the third screenshot with session 9's
placement: the logo, the stars and the lettering as before, and the two
buttons in the same place to within a source pixel, CRASH'N BURN lit and
PREVIEWS dimmed. Where the runtime's picture is flat (a pixel whose eight
neighbours are the same colour, inside each button), Phoenix's pixels at
the same places average (33, 25, 56) against the runtime's (32, 24, 57) on
the lit button's face (101 pixels) and (7, 8, 17) against (8, 8, 16) on the
dimmed one's (60 pixels): the pixel processor's two modes -- 1.5 times, and
17/32 -- come out as Phoenix draws them. The comparison script
(`cmp_dialog.py`) stays in the session's scratchpad.

## The Select Game menu (session 11)

With the pad (`pfboot --pad a@1300x1`), the runtime's run goes on past the
dialog to the intro movie and the Select Game menu (field 4478: Rally,
Tournament, Options). There is no Phoenix screenshot of it yet; the user,
looking at the field, confirmed it is the real game's menu.

## The race's start (session 13)

Three Phoenix screenshots of the race's start (Rally, Hammerhead, Crash
Course track 1, just after RACE; 953 x 686) set beside the runtime's fields
(320 x 241) scaled to that size with nearest neighbours. The grid is the game's `rand`
(`03-executables.md`), advanced once a field on the menus, so the user's
run and the runtime's agree only when the circuit is taken at the right
field: at 6356 the runtime has the user's grid (5th of 6). Then field 7547
matches the first shot (the HUD's numbers not yet written), 7600 the second
(5th / 6, the speed red), and 7740 the third, a few fields early (the start
given, the place "6" shown big, the purple car pulling away). Road, desert,
building, stripes, the cars ahead and alongside, the player's car and its
exhaust are where Phoenix has them, and alike to the eye at six times;
the shots are JPEGs of a scaled picture, so a one-pixel edge (the patent's
rule against Opera's) cannot be told from them.

Since session 14 the guest's clock counts the ARM60's clocks
(`03-executables.md`, "The guest's clock in the ARM60's clocks"), and the
fields move: the same grid comes with the circuit taken at 6405, then
presses at 7349 and 7549; the race starts at about 7602, and the fields
that matched the first two shots come again pixel for pixel at 7609 and
7655. The third shot's scene is at about 7810, the car a little faster
than at session 13's 7740.

**The radar out of its box** (session 14): the race's radar lines run
past the left of its box to the screen's edge in the runtime, on Phoenix
and on the user's FZ-10 alike, and in other players' recordings of the
game the user looked at (so not a matter of version or dump) -- GRAPHIX's `SetClipOrigin` refusing the
game's origin (`03-executables.md`). A glitch that looks like the port's
can be the original's: the console is the judge.

**The movies' smoothness** (the user: the window smoother than Phoenix,
the movies above all) is not the ARM60's speed: the intro movie decodes
all its 24 frames a second in about half the console's CPU time and
waits out the rest, at 1 us a safe point and in clocks alike. Played side
by side with the clock in clocks, the user found the window and Phoenix
**at par**: the same length, the same feel. Both slow down at the same
places in the movies -- frames the file itself holds longer
(`03-executables.md`, "The movie's pace is in the file").

The Rankout screen after the race (field 40,390 on: "RANKOUT: YOU FAILED
TO PLACE. 3 CONTINUES REMAIN.", CONTINUE and QUIT) has no Phoenix shot; the
user, looking at the fields, confirmed it is the real game's -- the chosen
option flickers by design, CONTINUE by default.

**The race's start, slower on the console** (session 14): the user's FZ-10
drops frames at the start of a race and recovers later on the circuit;
the runtime and Phoenix hold the frames from the start (Opera, on a
homebrew of the user's, did too). The runtime's clock counts the ARM60's
clocks but not the cel engine's work (`DrawCels` takes no guest time;
Opera's MADAM counts none either) nor the bus it shares: even on the CPU
alone the start is the hard part -- fields 7810-7930, about one frame in
five takes 3 fields instead of 2, against 5 in 500 later in the race --
and the cel engine's time would add most where the six cars are close.
**The user's choice: leave it.** The game's and the OS's code run
unchanged; running better than the console is not a fault of the port.
The line between this and the radar: this is a recompilation, not a
cycle-faithful emulator -- what the code does stays (the radar's clip is
the game's and the OS's logic), the hardware's limits do not (frames
dropped for want of time).
