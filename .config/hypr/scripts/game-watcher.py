#!/usr/bin/env python3
import os, pathlib, time
cfg = pathlib.Path.home() / ".config/hypr/perf-apps.txt"
prof = pathlib.Path("/sys/firmware/acpi/platform_profile")
state = pathlib.Path.home() / ".local/share/mocha-power-mode"
active = False
while True:
    try:
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
