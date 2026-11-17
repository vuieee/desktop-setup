#!/usr/bin/env python3
import json, pathlib, subprocess, time
import sys
if subprocess.run(["pgrep","-x","rofi"],capture_output=True).returncode==0: subprocess.run(["pkill","-x","rofi"]); sys.exit(0)
nl = chr(10)
home = pathlib.Path.home()
rc = home/".config/rofi/minimal.rasi"
pdir = home/".local/share/mocha-clipboard"
pdir.mkdir(parents=True, exist_ok=True)
pfile = pdir/"pins.json"
def load_pins():
    return json.loads(pfile.read_text()) if pfile.exists() else []
def save_pins(pins):
    pfile.write_text(json.dumps(pins, indent=2))
def rofi(prompt, items, w=540, lines=10, sel=0):
    cmd = ["rofi","-dmenu","-i","-p",prompt,"-selected-row",str(sel),"-selected-row",str(sel),"-theme",str(rc),"-theme-str",f"window {{ width: {w}px; }} mainbox {{ children: [listview]; }} listview {{ lines: {lines}; fixed-num-lines: true; padding: 0px; spacing: 0px; }}"]
    return subprocess.run(cmd,input=nl.join(items),text=True,capture_output=True).stdout.strip()
def img_mime(s):
    s = s.lower()
    return "image/jpeg" if "jpg" in s or "jpeg" in s else "image/webp" if "webp" in s else "image/gif" if "gif" in s else "image/png"
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
    hist = [l for l in subprocess.run(["cliphist","list"],text=True,capture_output=True).stdout.splitlines() if l.strip()]
    rows = ([f"{chr(0xf1f8)}  Clear Unpinned History"] if hist else []) + [f"{chr(0xf08d)}  [PIN {i+1}] {x[chr(100)+chr(105)+chr(115)+chr(112)]}" for i, x in enumerate(pins)]
    rows += [f"{chr(0xf0ea)}  {l.split(chr(9),1)[-1][:68]}" for l in hist[:40]]

    if not rows:
        rofi("clipboard", ["(Clipboard empty)"], 620, 12); break
    pick = rofi("clipboard", rows, 620, 12, (1 if hist else 0)+len(pins) if hist else 0)
    if not pick or pick == "(Clipboard empty)": break
    if "Clear Unpinned History" in pick:
        subprocess.run(["cliphist","wipe"]); continue
    if pick.startswith(chr(0xf08d)):
        idx = int(pick.split("[PIN ")[1].split("]")[0]) - 1
        item = pins[idx]
        act = rofi("pinned", [f"{chr(0xf0c5)}  Copy to Clipboard", f"{chr(0xf08d)}  Unpin Item"], 320, 2)
        if "Copy" in act:
            data = (pdir/item["file"]).read_bytes() if item["img"] else item["text"].encode()
            copy_bytes(data, item.get("mime","image/png") if item["img"] else "text/plain"); break
        elif "Unpin" in act:
            if item["img"]: (pdir/item["file"]).unlink(missing_ok=True)
            pins.pop(idx); save_pins(pins)
    else:
        sel_idx = rows.index(pick) - len(pins) - (1 if hist else 0)
        raw_line = hist[sel_idx]
        raw = subprocess.run(["cliphist","decode"],input=raw_line.encode(),capture_output=True).stdout
        is_img = "[[ binary data" in raw_line
        act = rofi("action", [f"{chr(0xf0c5)}  Copy to Clipboard", f"{chr(0xf08d)}  Pin Item", f"{chr(0xf1f8)}  Delete Entry"], 320, 3)
        if "Copy" in act:
            copy_bytes(raw, img_mime(raw_line) if is_img else "text/plain"); break
        elif "Pin" in act:
            fn = f"pin_{int(time.time()*1000)}.png"
            if is_img: (pdir/fn).write_bytes(raw)
            disp = raw_line.split(chr(9),1)[-1][:55]
            pins.insert(0, {"img": is_img, "file": fn if is_img else "", "text": "" if is_img else raw.decode(errors="replace"), "disp": disp, "mime": img_mime(raw_line) if is_img else "text/plain"})
            save_pins(pins)
        elif "Delete" in act:
            subprocess.run(["cliphist","delete"],input=raw_line,text=True)
