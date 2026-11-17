#!/usr/bin/env python3
import hashlib, pathlib, shutil, subprocess, sys
from PIL import Image, ImageOps

if subprocess.run(["pgrep", "-x", "rofi"], capture_output=True).returncode == 0:
    subprocess.run(["pkill", "-x", "rofi"])
    sys.exit(0)

home = pathlib.Path.home()
wdir = home / "wallpapers"
cdir = home / ".cache/mocha-wallpapers"
rc = home / ".config/rofi/minimal.rasi"
target = home / "Pictures/wallpaper.png"
hc = home / ".config/hypr/hyprpaper.conf"
wdir.mkdir(exist_ok=True)
cdir.mkdir(parents=True, exist_ok=True)

exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
walls = sorted([w for w in wdir.iterdir() if w.is_file() and w.suffix.lower() in exts], key=lambda w: w.name.lower())

if not walls:
    subprocess.run(["notify-send", "-a", "Wallpapers", "No Wallpapers Found", "Add images to ~/wallpapers"])
    sys.exit(0)

nul, sep, nl, q = chr(0), chr(31), chr(10), chr(34)
rows = []
for w in walls:
    st = w.stat()
    key = hashlib.md5(f"{w}:{st.st_mtime_ns}:{st.st_size}".encode()).hexdigest()
    tf = cdir / f"{key}.png"
    if not tf.exists():
        with Image.open(w) as im:
            card = ImageOps.fit(im.convert("RGB"), (220, 380), Image.Resampling.LANCZOS)
            card.save(tf, "PNG")
    rows.append(f"{w.stem}{nul}icon{sep}{tf}")

tstr = " ".join([
    "window { width: 1260px; padding: 18px; }",
    "mainbox { children: [listview]; }",
    "listview { columns: 5; lines: 1; spacing: 16px; fixed-height: true; fixed-columns: true; padding: 0px; }",
    "element { orientation: vertical; children: [element-icon, element-text]; padding: 8px; margin: 28px 0px; border: 2px; border-color: #595959; background-color: #000000; text-color: #808080; spacing: 8px; }",
    "element selected { margin: 0px; border: 2px; border-color: #ffffff; background-color: #000000; text-color: #ffffff; }",
    "element-icon { size: 210px; horizontal-align: 0.5; vertical-align: 0.5; background-color: transparent; }",
    f"element-text {{ horizontal-align: 0.5; font: {q}JetBrains Mono 11{q}; background-color: transparent; text-color: inherit; }}"
])

cmd = ["rofi", "-dmenu", "-i", "-show-icons", "-format", "i", "-kb-row-left", "Left,h", "-kb-row-right", "Right,l", "-theme", str(rc), "-theme-str", tstr]
res = subprocess.run(cmd, input=nl.join(rows), text=True, capture_output=True)
if res.returncode != 0 or not res.stdout.strip():
    sys.exit(0)

chosen = walls[int(res.stdout.strip())]
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(chosen, target)
hc.write_text(nl.join(["wallpaper {", "    monitor =", "    path = ~/Pictures/wallpaper.png", "    fit_mode = cover", "}", ""]))
subprocess.run(["pkill", "-x", "hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.Popen(["hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
subprocess.run(["notify-send", "-a", "Wallpapers", "Wallpaper Applied", chosen.name])
