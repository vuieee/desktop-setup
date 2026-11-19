#!/usr/bin/env python3
import os, pathlib, subprocess, time
cfg = pathlib.Path.home() / ".config/hypr/perf-apps.txt"
prof = pathlib.Path("/sys/firmware/acpi/platform_profile")
state = pathlib.Path.home() / ".local/share/mocha-power-mode"
acad = pathlib.Path("/sys/class/power_supply/ACAD/online")
menu = pathlib.Path.home() / ".config/waybar/scripts/power-profile-menu.py"
active = False
time.sleep(2)
last_ac = acad.read_text().strip() if acad.exists() else None
if last_ac in ("0", "1"):
    want = "balanced" if last_ac == "1" else "power-saver"
    cur_m = state.read_text().strip() if state.exists() else ""
    if cur_m != want:
        subprocess.run(["python3", str(menu), "--set", want])
while True:
    try:
        if acad.exists():
            cur_ac = acad.read_text().strip()
            if cur_ac != last_ac and cur_ac in ("0", "1"):
                last_ac = cur_ac
                subprocess.run(["python3", str(menu), "--set", "balanced" if cur_ac == "1" else "power-saver"])
                if active and prof.exists(): prof.write_text("performance")
        apps = {x.strip().lower() for x in cfg.read_text().splitlines() if x.strip()}
        procs = set()
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try: procs.add(pathlib.Path(f"/proc/{pid}/comm").read_text().strip().lower())
                except Exception: pass
        hit = bool(apps & procs)
        if hit and not active and prof.exists():
            prof.write_text("performance")
            active = True
        elif not hit and active and prof.exists():
            cur = state.read_text().strip() if state.exists() else "balanced"
            prof.write_text("quiet" if cur == "power-saver" else ("performance" if cur == "performance" else "balanced"))
            active = False
    except Exception: pass
    time.sleep(3)
