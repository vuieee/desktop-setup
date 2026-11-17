import pathlib,subprocess
h=pathlib.Path.home()
css=[("#000000","#ffffff"),("#ffffff","#000000"),("rgba(0, 0, 0, 0.72)","rgba(255, 255, 255, 0.72)"),("rgba(255, 255, 255, 0.72)","rgba(0, 0, 0, 0.72)"),("#000000b8","#ffffffb8"),("#ffffffb8","#000000b8"),("#dddddd","#222222"),("#222222","#dddddd"),("#b0b0b0","#505050"),("#505050","#b0b0b0"),("rgba(0, 0, 0, 0.35)","rgba(255, 255, 255, 0.35)"),("rgba(255, 255, 255, 0.35)","rgba(0, 0, 0, 0.35)"),("#010101","#fefefe"),("#fefefe","#010101"),("#555555","#aaaaaa"),("#aaaaaa","#555555")]
hp=[("rgba(ffffffff)","rgba(000000ff)"),("rgba(000000ff)","rgba(ffffffff)"),("rgba(595959aa)","rgba(a6a6a6aa)"),("rgba(a6a6a6aa)","rgba(595959aa)")]
def sw(t,m):
 for i,(a,_) in enumerate(m):t=t.replace(a,f"_T{i}_")
 for i,(_,b) in enumerate(m):t=t.replace(f"_T{i}_",b)
 return t
for f in ["waybar/style.css","rofi/minimal.rasi","swaync/style.css","hypr/scripts/osd-popup.py","kitty/kitty.conf","power-menu/power-menu.py","power-menu/fake-lock.py","yazi/theme.toml"]:
 fp=h/".config"/f
 if fp.exists():fp.write_text(sw(fp.read_text(),css))
hl=h/".config/hypr/hyprland.lua"
hl.write_text(sw(hl.read_text(),hp))
ff=h/".config/fastfetch/config.jsonc"
if ff.exists():ff.write_text(sw(ff.read_text(),[("white","black"),("black","white")]))
subprocess.run(["killall","-SIGUSR1","kitty"],stderr=-3)
dark = "background-color: #000000;" in (h / ".config/waybar/style.css").read_text().split("}")[0]
subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark" if dark else "prefer-light"], stderr=-3)
