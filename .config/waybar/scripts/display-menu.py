#!/usr/bin/env python3
import json, pathlib, re, subprocess

rc = pathlib.Path.home() / ".config/rofi/minimal.rasi"
hl = pathlib.Path.home() / ".config/hypr/hyprland.lua"

def rofi(lines, width=340, row=0):
    res = subprocess.run([
        "rofi", "-dmenu", "-i", "-selected-row", str(row), "-theme", str(rc),
        "-theme-str", f"window {{ width: {width}px; }} mainbox {{ children: [listview]; }} listview {{ lines: {min(len(lines), 10)}; padding: 0px; spacing: 0px; }}"
    ], input=chr(10).join(lines), text=True, capture_output=True)
    return res.stdout.strip()

def update_lua(mode_str, scale_str):
    t = hl.read_text()
    t = re.sub(r'(mode\s*=\s*")[^"]+(")', lambda m: m.group(1) + mode_str + m.group(2), t, count=1)
    t = re.sub(r'(scale\s*=\s*")[^"]+(")', lambda m: m.group(1) + scale_str + m.group(2), t, count=1)
    hl.write_text(t)
    subprocess.run(["hyprctl", "reload"], stdout=-3, stderr=-3)

def main():
    idx = 0
    while True:
        mons = json.loads(subprocess.check_output(["hyprctl", "monitors", "all", "-j"], text=True))
        mon = next((m for m in mons if m.get("focused")), mons.pop(0))
        name = mon["name"]
        w, h = mon["width"], mon["height"]
        hz = f"{mon['refreshRate']:.2f}Hz"
        raw_sc = mon["scale"]
        sc = "1.33" if abs(raw_sc - 1.3333334) < 0.01 else f"{raw_sc:.2f}".rstrip("0").rstrip(".")
        res_list, hz_list = [], []
        for m in mon.get("availableModes", []):
            rp, _, hp = m.partition("@")
            if rp and rp not in res_list: res_list.append(rp)
            if hp and hp not in hz_list: hz_list.append(hp)
        for fb in ("1920x1080", "1600x900", "1280x720"):
            if fb not in res_list: res_list.append(fb)
        if not hz_list: hz_list = ["165.00Hz", "60.00Hz"]
        cur_res = f"{w}x{h}"
        items = [
            f"\uf108  Display        {name:>10}",
            f"\uf065  Resolution     {cur_res:>10}",
            f"\uf0e7  Refresh Rate   {hz:>10}",
            f"\uf00e  Scale          {sc + 'x':>10}",
        ]
        ch = rofi(items, width=340, row=idx)
        if not ch: break
        if "Resolution" in ch:
            idx = 1
            rch = rofi([f"{r}  (active)" if r == cur_res else r for r in res_list], width=280)
            if rch:
                new_r = rch.split().pop(0)
                update_lua(f"{new_r}@{hz}", sc)
        elif "Refresh Rate" in ch:
            idx = 2
            hch = rofi([f"{x}  (active)" if x == hz else x for x in hz_list], width=280)
            if hch:
                new_h = hch.split().pop(0)
                update_lua(f"{cur_res}@{new_h}", sc)
        elif "Scale" in ch:
            idx = 3
            scales = ["1", "1.2", "1.25", "1.33", "1.5", "1.6", "1.75", "2"]
            sch = rofi([f"{s}x  (active)" if s == sc else f"{s}x" for s in scales], width=260)
            if sch:
                new_s = sch.split().pop(0).rstrip("x")
                update_lua(f"{cur_res}@{hz}", new_s)
        else:
            idx = 0

if __name__ == "__main__":
    main()
