#!/usr/bin/env python3
import glob, json, os, pathlib, re, subprocess, sys

ICONS = {"mouse": chr(0xf037d), "earbuds": chr(0xf02cb), "keyboard": chr(0xf030c)}

def classify(kind, name):
    t = f"{kind} {name}".lower()
    if any(k in t for k in ("mouse", "trackpad", "trackball", "mx master", "superlight", "viper", "deathadder", "basilisk", "orochi", "lamzu", "pulsar")):
        return "mouse"
    if any(k in t for k in ("headset", "headphone", "earbud", "earphone", "airpod", "buds", "jabra", "bose", "sennheiser", "moondrop", "audio")):
        return "earbuds"
    if any(k in t for k in ("keyboard", "keychron", "nuphy", "akko", "epomaker", "wooting", "ducky", "hhkb", "royal kludge")):
        return "keyboard"
    return None

def scan_upower():
    found = {}
    try:
        out = subprocess.check_output(["upower", "-d"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return found
    for b in out.split(chr(10) + "Device: ")[1:]:
        lns = b.splitlines()
        dev_path = lns[0].strip()
        if any(x in dev_path for x in ("DisplayDevice", "line_power", "battery_BAT")):
            continue
        model, kind, pct, present = "", "", None, True
        for ln in lns[1:]:
            s = ln.strip()
            if s.startswith("model:"): model = s.split(":", 1)[1].strip()
            elif s.startswith("native-path:") and not model: model = s.split(":", 1)[1].strip()
            elif s.startswith("present:"): present = s.split(":", 1)[1].strip().lower() == "yes"
            elif s.startswith("percentage:"):
                m = re.search(r"([0-9]+)", s)
                if m: pct = int(m.group(1))
            elif s in ("mouse", "keyboard", "headset", "headphones"):
                kind = s
        if not present or pct is None:
            continue
        cat = classify(kind, model)
        if cat:
            found[model or cat] = (cat, model or cat.title(), pct)
    return found

def scan_sysfs():
    found = {}
    for cap in glob.glob("/sys/class/power_supply/*/capacity"):
        base = os.path.dirname(cap)
        try:
            scope = open(os.path.join(base, "scope")).read().strip() if os.path.exists(os.path.join(base, "scope")) else ""
            if scope != "Device":
                continue
            pct = int(open(cap).read().strip())
            name = open(os.path.join(base, "model_name")).read().strip() if os.path.exists(os.path.join(base, "model_name")) else os.path.basename(base)
            cat = classify("", name)
            if cat:
                found[name] = (cat, name, pct)
        except Exception:
            continue
    return found

def scan_bt():
    found = {}
    try:
        devs = subprocess.check_output(["bluetoothctl", "devices", "Connected"], text=True, stderr=subprocess.DEVNULL).splitlines()
    except Exception:
        return found
    for d in devs:
        parts = d.split(" ", 2)
        if len(parts) < 3:
            continue
        mac, name = parts[1], parts[2].strip()
        cat = classify("", name)
        if not cat:
            continue
        try:
            info = subprocess.check_output(["bluetoothctl", "info", mac], text=True, stderr=subprocess.DEVNULL)
            m = re.search(r"Battery Percentage:\s*0x[0-9a-fA-F]+\s*\(([0-9]+)\)", info)
            if m:
                found[name] = (cat, name, int(m.group(1)))
        except Exception:
            continue
    return found

if "--test" in sys.argv:
    items = [("mouse", "Wireless Mouse", 85), ("earbuds", "Bluetooth Earbuds", 90), ("keyboard", "Wireless Keyboard", 75)]
else:
    merged = scan_bt()
    merged.update(scan_sysfs())
    merged.update(scan_upower())
    order = {"mouse": 0, "earbuds": 1, "keyboard": 2}
    items = sorted(merged.values(), key=lambda x: (order[x[0]], x[1].lower()))

if not items:
    print(json.dumps({"text": "", "tooltip": "", "class": "empty"}))
else:
    text = "  ".join(f"{ICONS[cat]} {pct}%" for cat, _, pct in items)
    tip = chr(10).join(f"{name}: {pct}%" for _, name, pct in items)
    cls = "low" if any(pct <= 20 for _, _, pct in items) else "connected"
    print(json.dumps({"text": text, "tooltip": tip, "class": cls}))
