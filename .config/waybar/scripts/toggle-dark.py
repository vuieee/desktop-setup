#!/usr/bin/env python3
import pathlib,subprocess
h=pathlib.Path.home()
nat=(h/".local/share/mocha-theme-bak/native").exists()
css=[("#1e1f24","#f2f3f7"),("#f2f3f7","#1e1f24"),("#dcdfe6","#23252c"),("#23252c","#dcdfe6"),("rgba(30, 31, 36, 0.75)","rgba(242, 243, 247, 0.75)"),("rgba(242, 243, 247, 0.75)","rgba(30, 31, 36, 0.75)"),("#1e1f24bf","#f2f3f7bf"),("#f2f3f7bf","#1e1f24bf"),("Adwaita-dark","Adwaita"),("Adwaita","Adwaita-dark"),("prefer-dark","prefer-light"),("prefer-light","prefer-dark")] if nat else [("#000000","#ffffff"),("#ffffff","#000000"),("rgba(0, 0, 0, 0.72)","rgba(255, 255, 255, 0.72)"),("rgba(255, 255, 255, 0.72)","rgba(0, 0, 0, 0.72)"),("#000000b8","#ffffffb8"),("#ffffffb8","#000000b8"),("#dddddd","#222222"),("#222222","#dddddd"),("#b0b0b0","#505050"),("#505050","#b0b0b0"),("rgba(0, 0, 0, 0.35)","rgba(255, 255, 255, 0.35)"),("rgba(255, 255, 255, 0.35)","rgba(0, 0, 0, 0.35)"),("#010101","#fefefe"),("#fefefe","#010101"),("#555555","#aaaaaa"),("#aaaaaa","#555555"),("Adwaita-dark","Adwaita"),("Adwaita","Adwaita-dark"),("prefer-dark","prefer-light"),("prefer-light","prefer-dark")]
hp=[("rgba(ffffffff)","rgba(000000ff)"),("rgba(000000ff)","rgba(ffffffff)"),("rgba(595959aa)","rgba(a6a6a6aa)"),("rgba(a6a6a6aa)","rgba(595959aa)")]
def sw(t,m):
 for i,(a,_) in enumerate(m): t=t.replace(a,f"_T{i}_")
 for i,(_,b) in enumerate(m): t=t.replace(f"_T{i}_",b)
 return t
fl=["waybar/style.css","rofi/minimal.rasi","swaync/style.css","hypr/scripts/osd-popup.py","kitty/kitty.conf","power-menu/power-menu.py","power-menu/fake-lock.py","gtk-3.0/settings.ini","gtk-4.0/settings.ini"] if nat else ["waybar/style.css","rofi/minimal.rasi","swaync/style.css","hypr/scripts/osd-popup.py","kitty/kitty.conf","power-menu/power-menu.py","power-menu/fake-lock.py","gtk-3.0/gtk.css","gtk-3.0/settings.ini","gtk-4.0/settings.ini","yazi/theme.toml","cava/config"]
for f in fl:
 fp=h/".config"/f
 if fp.exists(): fp.write_text(sw(fp.read_text(),css))
hl=h/".config/hypr/hyprland.lua"
hl.write_text(sw(hl.read_text(),hp))
ff=h/".config/fastfetch/config.jsonc"
if ff.exists(): ff.write_text(sw(ff.read_text(),[("white","black"),("black","white")]))
subprocess.run(["killall","-SIGUSR1","kitty"],stderr=-3)
w_full=(h/".config/waybar/style.css").read_text()
dark=not any(x in w_full for x in ("background-color: #ffffff;","rgba(255, 255, 255, 0.72)","background-color: #f2f3f7;","rgba(242, 243, 247, 0.75)"))
for s in ["gtk-3.0/settings.ini","gtk-4.0/settings.ini","yazi/theme.toml","cava/config"]:
 sp=h/".config"/s
 if sp.exists(): sp.write_text(sp.read_text().replace("prefer-dark-theme=0" if dark else "prefer-dark-theme=1","prefer-dark-theme=1" if dark else "prefer-dark-theme=0"))
subprocess.run(["gsettings","set","org.gnome.desktop.interface","gtk-theme","Adwaita-dark" if dark else "Adwaita"])
subprocess.run(["gsettings","set","org.gnome.desktop.interface","color-scheme","prefer-dark" if dark else "default"])
