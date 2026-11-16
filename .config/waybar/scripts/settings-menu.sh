#!/usr/bin/env python3
import pathlib, subprocess
nl = chr(10)
home = pathlib.Path.home()
wc, ws = home/".config/waybar/config.jsonc", home/".config/waybar/style.css"
rc, sc = home/".config/rofi/minimal.rasi", home/".config/swaync/style.css"
hl, osd = home/".config/hypr/hyprland.lua", home/".config/hypr/scripts/osd-popup.py"
top = subprocess.run(["rofi","-dmenu","-i","-theme",str(rc),"-theme-str","window { width: 200px; } mainbox { children: [listview]; } listview { lines: 4; padding: 0px; spacing: 0px; }"],input=nl.join([chr(0xf085)+"  System",chr(0xf1fc)+"  Appearance",chr(0xf09b)+"  GitHub",chr(0xf11c)+"  Keybinds"]),text=True,capture_output=True).stdout.strip()
if "GitHub" in top: subprocess.Popen(["python3","~/.config/waybar/scripts/github-menu.py"],start_new_session=True)
elif "Keybinds" in top: subprocess.Popen("rofi -dmenu -i -p keys -theme ~/.config/rofi/minimal.rasi -theme-str 'window { width: 720px; }' < ~/.config/hypr/cheatsheet.txt",shell=True,start_new_session=True)
elif "System" in top:
    sub = subprocess.run(["rofi","-dmenu","-i","-theme",str(rc),"-theme-str","window { width: 260px; } mainbox { children: [listview]; } listview { lines: 2; padding: 0px; spacing: 0px; }"],input=nl.join([chr(0xf0e7)+"  Auto-Boost Apps",chr(0xf2c9)+"  Fan & Thermal GUI"]),text=True,capture_output=True).stdout.strip()
    if "Auto-Boost Apps" in sub: subprocess.Popen(["~/.config/hypr/scripts/perf-apps-menu.sh"],start_new_session=True)
    elif "Fan & Thermal GUI" in sub: subprocess.Popen(["coolercontrol"],start_new_session=True)
elif "Appearance" in top:
    idx = 0
    while True:
        c, r, s, l, cfg, o = ws.read_text(), rc.read_text(), sc.read_text(), hl.read_text(), wc.read_text(), osd.read_text()
        dm = "Off" if "rgba(255, 255, 255, 0.72)" in c or "background: #ffffff;" in c.split("}")[0] else "On"
        ac = "On" if "0.72" in c else "Off"
        ps = "Bottom" if '"position": "bottom"' in cfg else "Top"
        ol = "On" if "border_size = 2" in l else "Off"
        rd = "On" if "rounding       = 10" in l else "Off"
        bg, fg = ("#000000","#ffffff") if dm=="On" else ("#ffffff","#000000")
        bgr, rfr = ("rgba(0, 0, 0, 0.72)","#000000b8") if dm=="On" else ("rgba(255, 255, 255, 0.72)","#ffffffb8")
        items = [((chr(0xf186) if dm=="On" else chr(0xf185))+"  Dark Mode",dm),(chr(0xf06e)+"  Acrylic",ac),(chr(0xf0c9)+"  Waybar",ps),(chr(0xf065)+"  Outlines",ol),((chr(0xf111) if rd=="On" else chr(0xf096))+"  Rounded",rd)]
        menu = nl.join(f"{k:<15}{v:>5}" for k, v in items)
        ch = subprocess.run(["rofi","-dmenu","-i","-selected-row",str(idx),"-theme",str(rc),"-theme-str","window { width: 280px; } mainbox { children: [listview]; } listview { lines: 5; padding: 0px; spacing: 0px; }"],input=menu,text=True,capture_output=True).stdout.strip()
        if not ch: break
        idx = ["Dark Mode","Acrylic","Waybar","Outlines","Rounded"].index(next(x for x in ["Dark Mode","Acrylic","Waybar","Outlines","Rounded"] if x in ch))
        if "Dark Mode" in ch:
            subprocess.run(["python3",str(home/".config/waybar/scripts/toggle-dark.py")])
            subprocess.run(["gsettings","set","org.gnome.desktop.interface","color-scheme","prefer-dark" if dm=="Off" else "default"],stderr=-3)
        elif "Acrylic" in ch:
            on = ch.endswith("Off")
            c = c.replace(f"background-color: {bg};",f"background-color: {bgr};") if on else c.replace(f"background-color: {bgr};",f"background-color: {bg};")
            r=r.replace("* {"+nl+f"    background-color: {bg};","* {"+nl+"    background-color: transparent;").replace("window {"+nl+"    width: 480px;","window {"+nl+f"    background-color: {rfr};{nl}    width: 480px;").replace(f"    background-color: {bg};{nl}    text-color: {fg};","    background-color: transparent;"+nl+f"    text-color: {fg};") if on else r.replace("* {"+nl+"    background-color: transparent;","* {"+nl+f"    background-color: {bg};").replace("window {"+nl+f"    background-color: {rfr};{nl}    width: 480px;","window {"+nl+"    width: 480px;").replace("    background-color: transparent;"+nl+f"    text-color: {fg};",f"    background-color: {bg};{nl}    text-color: {fg};")
            s=s.replace(f"background: {bg};",f"background: {bgr};").replace(".notification {"+nl+f"  background: {bgr};",".notification {"+nl+"  background: transparent;") if on else s.replace(f"background: {bgr};",f"background: {bg};").replace(".notification {"+nl+"  background: transparent;",".notification {"+nl+f"  background: {bg};")
            l = l.replace("active_opacity   = 1.0","active_opacity   = 0.85").replace("inactive_opacity = 1.0","inactive_opacity = 0.78") if on else l.replace("active_opacity   = 0.85","active_opacity   = 1.0").replace("inactive_opacity = 0.78","inactive_opacity = 1.0")
            mark = "-- mocha-acrylic-layers"
            lr = nl.join(["",mark,"hl.layer_rule({ name = 'mocha-waybar-blur', match = { namespace = 'waybar' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-rofi-blur', match = { namespace = 'rofi' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-cc-blur', match = { namespace = 'swaync-control-center' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-win-blur', match = { namespace = 'swaync-notification-window' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-osd-blur', match = { namespace = 'mocha-osd' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-fakelock-blur', match = { namespace = 'mocha-fakelock' }, blur = true, ignore_alpha = 0.1 })",""])
            l = next(iter(l.split(nl+mark))) + (lr if on else "")
            o = o.replace(f"background-color: {bg};",f"background-color: {bgr};") if on else o.replace(f"background-color: {bgr};",f"background-color: {bg};")
            ws.write_text(c); rc.write_text(r); sc.write_text(s); hl.write_text(l); osd.write_text(o)
        elif "Waybar" in ch:
            bot = ch.endswith("Top")
            cfg = cfg.replace('"position": "top"','"position": "bottom"').replace('"margin-top": 8','"margin-top": 0').replace('"margin-bottom": 0','"margin-bottom": 8') if bot else cfg.replace('"position": "bottom"','"position": "top"').replace('"margin-top": 0','"margin-top": 8').replace('"margin-bottom": 8','"margin-bottom": 0')
            wc.write_text(cfg)
        elif "Outlines" in ch:
            on = ch.endswith("Off")
            l = l.replace("border_size = 0,","border_size = 2,",1) if on else l.replace("border_size = 2,","border_size = 0,",1)
            c = c.replace("border: none; /* mocha-ol */",f"border: 2px solid {fg};") if on else c.replace(f"border: 2px solid {fg};","border: none; /* mocha-ol */")
            s = s.replace("border: none; /* mocha-ol */",f"border: 2px solid {fg};") if on else s.replace(f"border: 2px solid {fg};","border: none; /* mocha-ol */")
            r = r.replace("border: 0px; /* mocha-ol */","border: 2px;").replace("border: 0px; /* mocha-in */","border: 0px 0px 2px 0px;") if on else r.replace("border: 2px;","border: 0px; /* mocha-ol */").replace("border: 0px 0px 2px 0px;","border: 0px; /* mocha-in */")
            ws.write_text(c); rc.write_text(r); sc.write_text(s); hl.write_text(l)
        elif "Rounded" in ch:
            on = ch.endswith("Off")
            l = l.replace("rounding       = 0,","rounding       = 10,",1) if on else l.replace("rounding       = 10,","rounding       = 0,",1)
            c = c.replace("border-radius: 0;","border-radius: 10px;").replace("border-radius: 0px;","border-radius: 10px;") if on else c.replace("border-radius: 10px;","border-radius: 0;")
            s = s.replace("border-radius: 0px;","border-radius: 10px;") if on else s.replace("border-radius: 10px;","border-radius: 0px;")
            r = r.replace("border-radius: 0px;","border-radius: 10px;") if on else r.replace("border-radius: 10px;","border-radius: 0px;")
            ws.write_text(c); rc.write_text(r); sc.write_text(s); hl.write_text(l)
        subprocess.run(["hyprctl","reload"],stdout=-3,stderr=-3)
        subprocess.run(["swaync-client","-rs"],stdout=-3,stderr=-3)
        subprocess.run(["killall","waybar"],stdout=-3,stderr=-3)
        subprocess.run(["pkill","-f","osd-popup.py"],stdout=-3,stderr=-3)
        subprocess.Popen(["python3",str(osd)],stdout=-3,stderr=-3,start_new_session=True)
        subprocess.Popen(["waybar"],stdout=-3,stderr=-3,start_new_session=True)
