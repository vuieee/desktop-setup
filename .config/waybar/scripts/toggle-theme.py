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
dark=not any(x in ws_t for x in ("background-color: #ffffff;","rgba(255, 255, 255, 0.72)","background-color: #f2f3f7;","rgba(242, 243, 247, 0.75)"))
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
 to_mono=[("#1e1f24","#000000"),("#dcdfe6","#ffffff"),("rgba(30, 31, 36, 0.75)","rgba(0, 0, 0, 0.72)"),("#1e1f24bf","#000000b8")] if dark else [("#f2f3f7","#ffffff"),("#23252c","#000000"),("rgba(242, 243, 247, 0.75)","rgba(255, 255, 255, 0.72)"),("#f2f3f7bf","#ffffffb8")]
 for f in ui_files:
  fp=h/".config"/f
  if fp.exists(): fp.write_text(sw(fp.read_text(),to_mono))
 (bak/"native").unlink()
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
 to_nat=[("#000000","#1e1f24"),("#ffffff","#dcdfe6"),("rgba(0, 0, 0, 0.72)","rgba(30, 31, 36, 0.75)"),("#000000b8","#1e1f24bf")] if dark else [("#ffffff","#f2f3f7"),("#000000","#23252c"),("rgba(255, 255, 255, 0.72)","rgba(242, 243, 247, 0.75)"),("#ffffffb8","#f2f3f7bf")]
 for f in ui_files:
  fp=h/".config"/f
  if fp.exists(): fp.write_text(sw(fp.read_text(),to_nat))
 acc = chr(10).join(["",mark,"#battery { color: #4ade80; }","#battery.charging, #battery.plugged { color: #facc15; }","#battery.warning, #battery.critical { background: transparent; color: #f87171; }","#custom-power { color: #f87171; }","#wireplumber { color: #38bdf8; }","#bluetooth { color: #60a5fa; }","#network { color: #818cf8; }","#custom-caffeine { color: #fbbf24; }",""]) if dark else chr(10).join(["",mark,"#battery { color: #16a34a; }","#battery.charging, #battery.plugged { color: #ca8a04; }","#battery.warning, #battery.critical { background: transparent; color: #dc2626; }","#custom-power { color: #dc2626; }","#wireplumber { color: #0284c7; }","#bluetooth { color: #2563eb; }","#network { color: #4f46e5; }","#custom-caffeine { color: #d97706; }",""])
 ws_p.write_text(ws_p.read_text().split(mark)[0].rstrip()+chr(10)+acc)
 (bak/"native").touch()
subprocess.run(["killall","-SIGUSR1","kitty"],stderr=-3)
subprocess.run(["swaync-client","-rs"],stdout=-3,stderr=-3)
