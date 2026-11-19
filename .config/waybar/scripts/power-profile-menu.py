#!/usr/bin/env python3
import pathlib, subprocess, sys

nl = chr(10)
HOME = pathlib.Path.home()
RC = HOME / ".config/rofi/minimal.rasi"
PROF = pathlib.Path("/sys/firmware/acpi/platform_profile")
HL = HOME / ".config/hypr/hyprland.lua"
STATE = HOME / ".local/share/mocha-power-mode"

MODES = [
    ("power-saver", chr(0xf06c) + "  Power Saver",      "quiet",       "1920x1080@60.00Hz",  "Power Saver (60Hz + Quiet Fan)"),
    ("balanced",    chr(0xf24e) + "  Balanced",         "balanced",    "1920x1080@165.00Hz", "Balanced (165Hz + Balanced Fan)"),
    ("performance", chr(0xf0e7) + "  High Performance", "performance", "1920x1080@165.00Hz", "High Performance (165Hz + Max Fan)"),
]

if len(sys.argv) == 3 and sys.argv[1] == "--set":
    ch = next((lbl for k, lbl, _, _, _ in MODES if k == sys.argv[2]), "")
else:
    last = STATE.read_text().strip() if STATE.exists() else "balanced"
    idx = next((i for i, (k, _, _, _, _) in enumerate(MODES) if k == last), 1)
    opts = [lbl for _, lbl, _, _, _ in MODES]

    ch = subprocess.run(["rofi", "-dmenu", "-i", "-selected-row", str(idx), "-theme", str(RC), "-theme-str", "window { width: 250px; } mainbox { children: [listview]; } listview { lines: 3; padding: 0px; spacing: 0px; }"], input=nl.join(opts), text=True, capture_output=True).stdout.strip()
if not ch: raise SystemExit(0)

for key, lbl, prof_val, mon_mode, msg in MODES:
    if lbl == ch:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(key)
        try:
            if PROF.exists(): PROF.write_text(prof_val)
        except Exception as e:
            subprocess.run(["notify-send", "Power Profile Error", str(e)])
        hls = HL.read_text()
        for old_m in ("preferred", "1920x1080@60.00Hz", "1920x1080@165.00Hz"):
            hls = hls.replace(f'mode     = "{old_m}"', f'mode     = "{mon_mode}"', 1)
        HL.write_text(hls)
        subprocess.run(["hyprctl", "keyword", "monitor", f"eDP-1,{mon_mode},0x0,1.33"], stdout=-3, stderr=-3)
        subprocess.run(["hyprctl", "reload"], stdout=-3, stderr=-3)
        subprocess.run(["notify-send", "Power Profile", msg])
        break
