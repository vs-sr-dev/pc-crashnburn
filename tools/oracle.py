"""Crash 'n Burn in Opera (RetroArch), driven from here: the oracle for what
the port shows and for what the game prints.

    python tools/oracle.py [--at SECONDS:WHAT,...] [--out DIR] [--quit SECONDS] [--record]

Boots iso/*.cue in RetroArch's Opera core with the panafz10 BIOS. At each
time given (seconds since the launch, the emulator running at its own
speed) it does WHAT:

    shot                      a screenshot, saved as DIR/t<SECONDS>.png
    P / A+C / ...             press these buttons (3DO names: UP DOWN LEFT
                              RIGHT A B C L R P X) for 0.15 s

The game's own debug output -- its 122 `kprintf` call sites -- reaches
RetroArch's log through the core's `opera_kprint`; the run keeps it as
DIR/kprintf.txt, one line a print, in order. That is what the port's
runtime prints too, so the two can be compared line for line.

RetroArch is driven over UDP: its command port (55355) takes SCREENSHOT and
QUIT, its network RetroPad (55400 for user 1) the buttons. The run leaves
RetroArch's own settings alone: an --appendconfig file in DIR gives it its
own save folder (emptied first, so every run starts with an empty NVRAM),
its own core options (the user's, with `opera_kprint` on and the BIOS
pinned), the network RetroPad, RetroAchievements off (the user's account is
not touched by test runs), and no saving of the configuration on exit.
RetroArch's own output is kept as DIR/console.txt.

--record has RetroArch record the run (DIR/record.mkv) and keeps the sound
of it as DIR/record.wav (ffmpeg on the PATH).

The 3DO pad on the RetroPad follows the core's input descriptors (A on Y,
B on B, C on A, P on START, X on SELECT): to be confirmed on the first run
that presses them. The times are wall-clock times, so two runs differ by a
few frames.
"""
import argparse
import glob
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import time
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
RA_DIR = r"F:\RetroArch 2"
RETROARCH = os.path.join(RA_DIR, "retroarch.exe")
CORE = os.path.join(RA_DIR, "cores", "opera_libretro.dll")
USER_OPTS = os.path.join(RA_DIR, "config", "Opera", "Opera.opt")
RETROBIOS = r"D:\Homebrew6\retrobios-main.zip"
RETROBIOS_3DO = "retrobios-main/bios/3DO Company/3DO/"
CMD_PORT = 55355
REMOTE_PORT = 55400

# libretro's joypad ids, and the 3DO pad on them
RETROPAD = {"B": 0, "Y": 1, "SELECT": 2, "START": 3, "UP": 4, "DOWN": 5, "LEFT": 6, "RIGHT": 7,
            "A": 8, "X": 9, "L": 10, "R": 11}
PAD3DO = {"UP": "UP", "DOWN": "DOWN", "LEFT": "LEFT", "RIGHT": "RIGHT",
          "A": "Y", "B": "B", "C": "A", "L": "L", "R": "R", "P": "START", "X": "SELECT"}
OPTS = {"opera_bios": "panafz10.bin", "opera_kprint": "enabled", "opera_swi_hle": "disabled",
        "opera_nvram_storage": "per game", "opera_region": "ntsc"}


def setup(out):
    saves = os.path.join(out, "saves")
    shots = os.path.join(out, "screenshots")
    for d in (saves, shots):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    opts = os.path.join(out, "opera.opt")
    lines = []
    if os.path.exists(USER_OPTS):
        lines = [l.rstrip("\n") for l in open(USER_OPTS)
                 if l.split("=")[0].strip() not in OPTS]
    with open(opts, "w") as f:
        f.write("\n".join(lines + ['%s = "%s"' % kv for kv in OPTS.items()]) + "\n")
    append = os.path.join(out, "append.cfg")
    with open(append, "w") as f:
        for k, v in (("savefile_directory", saves), ("savestate_directory", saves),
                     ("screenshot_directory", shots), ("core_options_path", opts),
                     ("game_specific_options", "false"), ("global_core_options", "true"),
                     ("config_save_on_exit", "false"), ("network_cmd_enable", "true"),
                     ("network_cmd_port", str(CMD_PORT)), ("network_remote_enable", "true"),
                     ("network_remote_enable_user_p1", "true"),
                     ("network_remote_base_port", str(REMOTE_PORT)),
                     ("pause_nonactive", "false"), ("savestate_thumbnail_enable", "false"),
                     ("log_verbosity", "true"), ("libretro_log_level", "0"),
                     ("cheevos_enable", "false")):
            f.write('%s = "%s"\n' % (k, v))
    return append, shots


def kprintf_lines(log):
    """The core's kprint lines out of RetroArch's log, prefixes removed."""
    out = []
    for line in open(log, encoding="utf-8", errors="replace"):
        m = re.match(r"^\[(?:libretro )?(?:INFO|DEBUG|WARN)\]\s*(?:\[opera\]\s*)?(?:\[kprint\]\s*)?(.*)$",
                     line.rstrip("\n"))
        if m and "kprint" in line.lower():
            out.append(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--at", default="", help="SECONDS:WHAT,... (WHAT: shot, or buttons joined by +)")
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "oracle"))
    ap.add_argument("--quit", type=float, default=None, help="quit at this time (default: after the last event)")
    ap.add_argument("--record", action="store_true", help="record the run, keep its sound as DIR/record.wav")
    ap.add_argument("--opt", action="append", default=[], metavar="KEY=VALUE",
                    help="a core option for this run, e.g. opera_swi_hle=enabled")
    ap.add_argument("--bios", help="a BIOS file name from the retrobios archive (e.g. panafz1.bin), "
                                   "given to this run in a system folder of its own")
    a = ap.parse_args()
    for kv in a.opt:
        k, v = kv.split("=", 1)
        OPTS[k.strip()] = v.strip()
    system = None
    if a.bios:
        system = os.path.join(os.path.abspath(a.out), "system")
        os.makedirs(system, exist_ok=True)
        with zipfile.ZipFile(RETROBIOS) as z:
            for n in z.namelist():
                if n.startswith(RETROBIOS_3DO) and n.endswith(".bin") and os.path.basename(n):
                    with open(os.path.join(system, os.path.basename(n)), "wb") as f:
                        f.write(z.read(n))
        if not os.path.exists(os.path.join(system, a.bios)):
            sys.exit("no %s in the retrobios archive" % a.bios)
        OPTS["opera_bios"] = a.bios
    cues = glob.glob(os.path.join(ROOT, "iso", "*.cue"))
    if not cues:
        sys.exit("no .cue in iso/")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    append, shots = setup(out)
    if system:
        with open(append, "a") as f:
            f.write('system_directory = "%s"\n' % system)
    events = []
    for item in filter(None, a.at.split(",")):
        t, what = item.split(":", 1)
        events.append((float(t), what))
    events.sort()
    quit_at = a.quit if a.quit is not None else (events[-1][0] + 1 if events else 10)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def command(c):
        sock.sendto(c.encode(), ("127.0.0.1", CMD_PORT))

    def buttons(names, state):
        for n in names:
            if n not in PAD3DO:
                sys.exit("no 3DO button %s" % n)
            msg = struct.pack("<iiiiH2x", 0, 1, 0, RETROPAD[PAD3DO[n]], state)   # port, device, index, id, state
            sock.sendto(msg, ("127.0.0.1", REMOTE_PORT))

    log = os.path.join(out, "retroarch.log")
    cmd = [RETROARCH, "-L", CORE, os.path.abspath(cues[0]), "--appendconfig=" + append, "-v",
           "--log-file=" + log]
    mkv = os.path.join(out, "record.mkv")
    if a.record:
        if os.path.exists(mkv):
            os.remove(mkv)
        cmd += ["--record", mkv]
    console = open(os.path.join(out, "console.txt"), "w")
    p = subprocess.Popen(cmd, stdout=console, stderr=subprocess.STDOUT)
    t0 = time.monotonic()
    releases = []
    shot_times = []
    try:
        pending = list(events)
        while True:
            now = time.monotonic() - t0
            for r in [r for r in releases if r[0] <= now]:
                buttons(r[1], 0)
                releases.remove(r)
            while pending and pending[0][0] <= now:
                t, what = pending.pop(0)
                if what == "shot":
                    command("SCREENSHOT")
                    shot_times.append(t)
                else:
                    names = what.split("+")
                    buttons(names, 1)
                    releases.append((now + 0.15, names))
            if now >= quit_at or p.poll() is not None:
                break
            time.sleep(0.005)
    finally:
        command("QUIT")
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
        console.close()
    files = sorted(os.listdir(shots), key=lambda n: os.path.getmtime(os.path.join(shots, n)))
    for t, n in zip(shot_times, files):
        dst = os.path.join(out, "t%g.png" % t)
        shutil.move(os.path.join(shots, n), dst)
        print("%6.1f s: %s" % (t, dst))
    if len(files) != len(shot_times):
        print("%d screenshots asked for, %d came" % (len(shot_times), len(files)))
    if os.path.exists(log):
        lines = kprintf_lines(log)
        with open(os.path.join(out, "kprintf.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))
        print("kprintf: %d lines in %s" % (len(lines), os.path.join(out, "kprintf.txt")))
    if a.record and os.path.exists(mkv):
        wav = os.path.join(out, "record.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mkv, "-vn", "-acodec", "pcm_s16le", wav],
                       check=True)
        print("sound: %s" % wav)


if __name__ == "__main__":
    main()
