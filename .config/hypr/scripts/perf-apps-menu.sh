#!/usr/bin/env python3
import os, pathlib, shlex, subprocess
nl = chr(10)
home = pathlib.Path.home()
cfg = home / ".config/hypr/perf-apps.txt"
rc = home / ".config/rofi/minimal.rasi"
cfg.touch(exist_ok=True)
saved = [x.strip() for x in cfg.read_text().splitlines() if x.strip()]
found = {}
for d in (pathlib.Path("/usr/share/applications"), home / ".local/share/applications"):
    if d.exists():
        for f in d.glob("*.desktop"):
            try:
                nm, ex = None, None
                for line in f.read_text(errors="ignore").splitlines():
                    if line.startswith("Name=") and not nm: nm = line.split("=", 1)[1]
                    elif line.startswith("Exec=") and not ex: ex = line.split("=", 1)[1]
                if nm and ex:
                    parts = [p for p in shlex.split(ex) if not p.startswith("%") and "=" not in p]
                    if parts:
                        bin_name = os.path.basename(parts[0])
                        if bin_name not in ("env", "sh", "bash", "steam"):
                            found[f"+ {nm} ({bin_name})"] = bin_name
            except Exception:
                pass
items = [f"- {x} (remove)" for x in saved] + sorted(found.keys())
res = subprocess.run(["rofi", "-dmenu", "-i", "-theme", str(rc), "-theme-str", "entry { placeholder: 'search app for performance mode'; }"], input=nl.join(items), text=True, capture_output=True)
ch = res.stdout.strip()
if ch.startswith("- "):
    rem = ch[2:-9]
    cfg.write_text(nl.join([x for x in saved if x != rem]) + nl)
elif ch in found:
    val = found[ch]
    if val not in saved: saved.append(val)
    cfg.write_text(nl.join(saved) + nl)
elif ch:
    if ch not in saved: saved.append(ch)
    cfg.write_text(nl.join(saved) + nl)
