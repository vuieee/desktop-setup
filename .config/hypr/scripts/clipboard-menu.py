#!/usr/bin/env python3
import json, pathlib, subprocess, time, sys

if subprocess.run(["pgrep", "-x", "rofi"], capture_output=True).returncode == 0:
    subprocess.run(["pkill", "-x", "rofi"])
    sys.exit(0)

nl = chr(10)
nul = chr(0)
sep = chr(31)
home = pathlib.Path.home()
rc = home / ".config/rofi/minimal.rasi"
pdir = home / ".local/share/mocha-clipboard"
tdir = home / ".cache/mocha-clipboard-thumbs"
pdir.mkdir(parents=True, exist_ok=True)
tdir.mkdir(parents=True, exist_ok=True)
pfile = pdir / "pins.json"

def load_pins():
    return json.loads(pfile.read_text()) if pfile.exists() else []

def save_pins(pins):
    pfile.write_text(json.dumps(pins, indent=2))

def rofi(prompt, items, w=620, lines=None, sel=0, icons=False):
    n = max(1, min(len(items), lines if lines is not None else 12))
    tstr = (
        f"window {{ width: {w}px; }} "
        f"mainbox {{ children: [listview]; }} "
        f"listview {{ lines: {n}; fixed-num-lines: true; padding: 0px; spacing: 0px; }} "
        f"element {{ children: [element-text, element-icon]; spacing: 10px; }} "
        f"element-icon {{ size: {36 if icons else 0}px; background-color: transparent; }} "
        f"element-text {{ expand: true; vertical-align: 0.5; }}" + (" element selected {{ background-color: #000000; text-color: #808080; }}" if items == ["(Clipboard empty)"] else "")
    )
    cmd = ["rofi", "-dmenu", "-i", "-p", prompt, "-selected-row", str(sel), "-theme", str(rc), "-theme-str", tstr]
    if icons:
        cmd.append("-show-icons")
    res = subprocess.run(cmd, input=nl.join(items), text=True, capture_output=True)
    return res.returncode, res.stdout.strip()

def img_mime(s):
    s = s.lower()
    return "image/jpeg" if "jpg" in s or "jpeg" in s else "image/webp" if "webp" in s else "image/gif" if "gif" in s else "image/png"

def thumb_for(raw_line):
    cid = next(iter(raw_line.split(chr(9), 1))).strip()
    tf = tdir / f"{cid}.png"
    if not tf.exists():
        raw = subprocess.run(["cliphist", "decode"], input=raw_line.encode(), capture_output=True).stdout
        if raw:
            tf.write_bytes(raw)
    return str(tf) if tf.exists() else ""

def copy_bytes(data, mime="text/plain"):
    subprocess.run(["pkill", "-x", "wl-copy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp = pathlib.Path("/tmp/mocha-clip-restore")
    tmp.write_bytes(data)
    f = open(tmp, "rb")
    subprocess.Popen(["wl-copy", "--type", mime], stdin=f, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
    f.close()
    if mime.startswith("image/") and subprocess.run(["which", "xclip"], stdout=subprocess.DEVNULL).returncode == 0:
        fx = open(tmp, "rb")
        subprocess.Popen(["xclip", "-selection", "clipboard", "-t", mime], stdin=fx, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
        fx.close()
    time.sleep(0.08)

while True:
    pins = load_pins()
    hist = [l for l in subprocess.run(["cliphist", "list"], text=True, capture_output=True).stdout.splitlines() if l.strip()]
    display_rows = []
    rofi_rows = []
    has_any_icon = False

    if hist:
        lbl = f"{chr(0xf1f8)}  Clear Unpinned History"
        display_rows.append(lbl)
        rofi_rows.append(lbl)

    for i, x in enumerate(pins):
        lbl = f"{chr(0xf08d)}  [PIN {i+1}] {x[chr(100)+chr(105)+chr(115)+chr(112)]}"
        display_rows.append(lbl)
        if x.get("img") and x.get("file") and (pdir / x["file"]).exists():
            rofi_rows.append(f"{lbl}{nul}icon{sep}{pdir / x[chr(102)+chr(105)+chr(108)+chr(101)]}")
            has_any_icon = True
        else:
            rofi_rows.append(lbl)

    for l in hist[:40]:
        lbl = f"{chr(0xf0ea)}  {l.split(chr(9), 1)[-1][:68]}"
        display_rows.append(lbl)
        if "[[ binary data" in l:
            tp = thumb_for(l)
            if tp:
                rofi_rows.append(f"{lbl}{nul}icon{sep}{tp}")
                has_any_icon = True
            else:
                rofi_rows.append(lbl)
        else:
            rofi_rows.append(lbl)

    if not display_rows:
        rofi("clipboard", ["(Clipboard empty)"], 620, 1, 0, False)
        break

    default_sel = ((1 if hist else 0) + len(pins)) if hist else 0
    rc_code, pick = rofi("clipboard", rofi_rows, 620, min(len(display_rows), 12), default_sel, has_any_icon)
    if rc_code != 0 or not pick or pick == "(Clipboard empty)":
        break

    if "Clear Unpinned History" in pick:
        subprocess.run(["cliphist", "wipe"])
        for f in tdir.glob("*.png"):
            f.unlink(missing_ok=True)
        continue

    if pick.startswith(chr(0xf08d)):
        idx = int(next(iter(pick.partition("[PIN ")[2].partition("]")))) - 1
        item = pins[idx]
        _, act = rofi("pinned", [f"{chr(0xf0c5)}  Copy to Clipboard", f"{chr(0xf08d)}  Unpin Item"], 320, 2, 0, False)
        if "Copy" in act:
            data = (pdir / item["file"]).read_bytes() if item["img"] else item["text"].encode()
            copy_bytes(data, item.get("mime", "image/png") if item["img"] else "text/plain")
            break
        elif "Unpin" in act:
            if item["img"] and item.get("file"):
                (pdir / item["file"]).unlink(missing_ok=True)
            pins.pop(idx)
            save_pins(pins)
    else:
        sel_idx = display_rows.index(pick) - len(pins) - (1 if hist else 0)
        raw_line = hist[sel_idx]
        raw = subprocess.run(["cliphist", "decode"], input=raw_line.encode(), capture_output=True).stdout
        is_img = "[[ binary data" in raw_line
        _, act = rofi("action", [f"{chr(0xf0c5)}  Copy to Clipboard", f"{chr(0xf08d)}  Pin Item", f"{chr(0xf1f8)}  Delete Entry"], 320, 3, 0, False)
        if "Copy" in act:
            copy_bytes(raw, img_mime(raw_line) if is_img else "text/plain")
            break
        elif "Pin" in act:
            fn = f"pin_{int(time.time()*1000)}.png"
            if is_img:
                (pdir / fn).write_bytes(raw)
            disp = raw_line.split(chr(9), 1)[-1][:55]
            pins.insert(0, {"img": is_img, "file": fn if is_img else "", "text": "" if is_img else raw.decode(errors="replace"), "disp": disp, "mime": img_mime(raw_line) if is_img else "text/plain"})
            save_pins(pins)
        elif "Delete" in act:
            cid = next(iter(raw_line.split(chr(9), 1))).strip()
            (tdir / f"{cid}.png").unlink(missing_ok=True)
            subprocess.run(["cliphist", "delete"], input=raw_line, text=True)
