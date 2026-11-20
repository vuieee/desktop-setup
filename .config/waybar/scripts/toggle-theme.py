#!/usr/bin/env python3
import json,pathlib,shutil,subprocess
h=pathlib.Path.home()
bak=h/".local/share/mocha-theme-bak"
app_files=["gtk-3.0/gtk.css","gtk-4.0/gtk.css","yazi/theme.toml","micro/settings.json","cava/config"]
ui_files=["waybar/style.css","rofi/minimal.rasi","swaync/style.css","hypr/scripts/osd-popup.py","kitty/kitty.conf","power-menu/power-menu.py","power-menu/fake-lock.py"]
def sw(t,m):
 for i,(a,_) in enumerate(m): t=t.replace(a,f"_T{i}_")
 for i,(_,b) in enumerate(m): t=t.replace(f"_T{i}_",b)
 return t
ws_p=h/".config/waybar/style.css"
ws_t=ws_p.read_text()
dark=not any(x in ws_t for x in ("background-color: #ffffff;","rgba(255, 255, 255, 0.72)","background-color: #f8fafc;","rgba(248, 250, 252, 0.78)"))
mark="/* mocha-default-accents */"
if (bak/"native").exists():
 for f in app_files:
  src=bak/f; dst=h/".config"/f
  if src.exists(): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
  elif dst.exists(): dst.unlink()
 if not dark:
  am=[("#000000","#ffffff"),("#ffffff","#000000"),("#555555","#aaaaaa"),("#aaaaaa","#555555")]
  for f in app_files:
   fp=h/".config"/f
   if fp.exists(): fp.write_text(sw(fp.read_text(),am))
 if mark in ws_t:
  ws_p.write_text(ws_t.split(mark)[0].rstrip()+chr(10))
 to_mono=[("#1e222d","#000000"),("#f1f5f9","#ffffff"),("rgba(30, 34, 45, 0.78)","rgba(0, 0, 0, 0.72)"),("#1e222dbf","#000000b8")] if dark else [("#f8fafc","#ffffff"),("#0f172a","#000000"),("rgba(248, 250, 252, 0.78)","rgba(255, 255, 255, 0.72)"),("#f8fafcbf","#ffffffb8")]
 for f in ui_files:
  fp=h/".config"/f
  if fp.exists(): fp.write_text(sw(fp.read_text(),to_mono))
 hl_p = h / ".config/hypr/hyprland.lua"; hl_p.write_text(hl_p.read_text().replace("border_size = 1,", "border_size = 2,", 1).replace("rgba(64748bff)", "rgba(ffffffff)").replace("rgba(94a3b8ff)", "rgba(000000ff)").replace("rgba(334155aa)", "rgba(595959aa)").replace("rgba(cbd5e1aa)", "rgba(a6a6a6aa)")); [p.write_text(p.read_text().replace("1px solid #64748b", "2px solid #ffffff").replace("1px solid #94a3b8", "2px solid #000000").replace("border-color: #64748b;", "border-color: #ffffff;").replace("border-color: #94a3b8;", "border-color: #000000;").replace("1px solid", "2px solid").replace("border: 1px;", "border: 2px;").replace("0px 0px 1px 0px", "0px 0px 2px 0px")) for p in [ws_p, h/".config/swaync/style.css", h/".config/rofi/minimal.rasi", h/".config/hypr/scripts/osd-popup.py"] if p.exists()]; subprocess.run(["hyprctl", "reload"], stdout=-3, stderr=-3); ff_p = h / ".config/fastfetch/config.jsonc"; ffd = json.loads(ff_p.read_text()); ffd["logo"]["source"] = "~/.config/fastfetch/logo/" + ("cachyos-light.png" if dark else "cachyos-dark.png"); ffd["display"]["color"] = "default"; raw_ff = json.dumps(ffd, indent=4).replace("\u001b[36m", "").replace("\u001b[39m", "").replace("\u001b[1;33m", "\u001b[1m").replace("\u001b[22;39m", "\u001b[22m").replace("\u001b[1;31m", ""); ff_p.write_text(raw_ff + chr(10)); (bak/"native").unlink()
else:
 bak.mkdir(parents=True,exist_ok=True)
 for f in app_files:
  src=h/".config"/f; dst=bak/f
  if src.exists():
   dst.parent.mkdir(parents=True,exist_ok=True); t=src.read_text()
   if not dark:
    am=[("#ffffff","#000000"),("#000000","#ffffff"),("#aaaaaa","#555555"),("#555555","#aaaaaa")]
    t=sw(t,am)
   dst.write_text(t)
 (h/".config/gtk-3.0/gtk.css").write_text("")
 (h/".config/gtk-4.0/gtk.css").write_text("")
 yt=h/".config/yazi/theme.toml"
 if yt.exists(): yt.unlink()
 ms=h/".config/micro/settings.json"
 if ms.exists(): d=json.loads(ms.read_text()); d["colorscheme"]="default"; ms.write_text(json.dumps(d,indent=2)+chr(10))
 cc=h/".config/cava/config"
 if cc.exists(): cc.write_text(chr(10).join(l for l in cc.read_text().splitlines() if not l.startswith("foreground ="))+chr(10))
 to_nat=[("#000000","#1e222d"),("#ffffff","#f1f5f9"),("rgba(0, 0, 0, 0.72)","rgba(30, 34, 45, 0.78)"),("#000000b8","#1e222dbf")] if dark else [("#ffffff","#f8fafc"),("#000000","#0f172a"),("rgba(255, 255, 255, 0.72)","rgba(248, 250, 252, 0.78)"),("#ffffffb8","#f8fafcbf")]
 for f in ui_files:
  fp=h/".config"/f
  if fp.exists(): fp.write_text(sw(fp.read_text(),to_nat))
 acc = chr(10).join(["",mark,"#battery { color: #4ade80; }","#battery.charging, #battery.plugged { color: #facc15; }","#battery.warning, #battery.critical { background: transparent; color: #f87171; }","#custom-power { color: #f87171; }","#wireplumber { color: #38bdf8; }","#bluetooth { color: #60a5fa; }","#network { color: #818cf8; }","#custom-caffeine { color: #fbbf24; }",""]) if dark else chr(10).join(["",mark,"#battery { color: #16a34a; }","#battery.charging, #battery.plugged { color: #ca8a04; }","#battery.warning, #battery.critical { background: transparent; color: #dc2626; }","#custom-power { color: #dc2626; }","#wireplumber { color: #0284c7; }","#bluetooth { color: #2563eb; }","#network { color: #4f46e5; }","#custom-caffeine { color: #d97706; }",""])
 ws_p.write_text(ws_p.read_text().split(mark)[0].rstrip()+chr(10)+acc)
 hl_p = h / ".config/hypr/hyprland.lua"; bd = "#64748b" if dark else "#94a3b8"; bda = "rgba(64748bff)" if dark else "rgba(94a3b8ff)"; bdi = "rgba(334155aa)" if dark else "rgba(cbd5e1aa)"; hl_p.write_text(hl_p.read_text().replace("border_size = 2,", "border_size = 1,", 1).replace("rgba(ffffffff)", bda).replace("rgba(000000ff)", bda).replace("rgba(595959aa)", bdi).replace("rgba(a6a6a6aa)", bdi)); [p.write_text(p.read_text().replace("2px solid #ffffff", f"1px solid {bd}").replace("2px solid #000000", f"1px solid {bd}").replace("border-color: #ffffff;", f"border-color: {bd};").replace("border-color: #000000;", f"border-color: {bd};").replace("2px solid", "1px solid").replace("border: 2px;", "border: 1px;").replace("0px 0px 2px 0px", "0px 0px 1px 0px")) for p in [ws_p, h/".config/swaync/style.css", h/".config/rofi/minimal.rasi", h/".config/hypr/scripts/osd-popup.py"] if p.exists()]; subprocess.run(["hyprctl", "reload"], stdout=-3, stderr=-3); ff_p = h / ".config/fastfetch/config.jsonc"; ffd = json.loads(ff_p.read_text()); ffd["logo"]["source"] = "~/.config/fastfetch/logo/cachyos.png"; ffd["display"]["color"] = "default"; ks = ["OS","Kernel","Shell","WM","Ram","CPU","GPU","Disk1","Disk2","Packages"]; [m.update({"key": m["key"].replace(k, f"[36m{k}[39m", 1)}) for m in ffd["modules"] if isinstance(m, dict) and "key" in m for k in ks if f"  {k}" in m["key"]]; [m.update({"format": "╰─── [1;33mBLAZINGLY FAST ![22;39m ── [1;31m圧倒的爆速！[22;39m ────╯"}) for m in ffd["modules"] if isinstance(m, dict) and "BLAZINGLY FAST" in m.get("format", "")]; ff_p.write_text(json.dumps(ffd, indent=4) + chr(10)); (bak/"native").touch()
subprocess.run(["killall","-SIGUSR1","kitty"],stderr=-3)
subprocess.run(["swaync-client","-rs"],stdout=-3,stderr=-3)
