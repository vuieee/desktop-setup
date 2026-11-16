#!/usr/bin/env python3
import os, pathlib, time
cfg = pathlib.Path.home() / ".config/hypr/perf-apps.txt"
prof = pathlib.Path("/sys/firmware/acpi/platform_profile")
active = False
while True:
    try:
        apps = {x.strip().lower() for x in cfg.read_text().splitlines() if x.strip()}
        procs = set()
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                try:
                    c = pathlib.Path(f"/proc/{pid}/comm").read_text().strip().lower()
                    procs.add(c)
                except Exception:
                    pass
        hit = bool(apps & procs)
        if hit and not active and prof.exists():
            prof.write_text("performance")
            active = True
        elif not hit and active and prof.exists():
            prof.write_text("balanced")
            active = False
    except Exception:
        pass
    time.sleep(3)
