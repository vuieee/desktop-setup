#!/usr/bin/env python3
import json, pathlib, subprocess, sys, time

def running():
    return subprocess.run(["pgrep", "-x", "hypridle"], stdout=subprocess.DEVNULL).returncode == 0

if len(sys.argv) > 1 and sys.argv[1] == "toggle":
    if running():
        subprocess.run(["pkill", "-x", "hypridle"])
        time.sleep(0.1)
        subprocess.run(["notify-send", "-a", "Caffeine", "Caffeine ON", "Idle sleep and auto-lock paused"])
    else:
        subprocess.Popen(["hypridle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(0.1)
        subprocess.run(["notify-send", "-a", "Caffeine", "Caffeine OFF", "Idle sleep and auto-lock active"])
    subprocess.run(["pkill", "-RTMIN+8", "waybar"])
else:
    active = not running()
    icon = chr(0xf0f4)
    label = f"{icon}  ON" if active else f"{icon}  OFF"
    tip = "Caffeine ON (Idle paused)" if active else "Caffeine OFF (Idle active)"
    print(json.dumps({"text": label, "tooltip": tip, "class": "active" if active else "inactive"}))
