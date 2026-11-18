#!/usr/bin/env python3
import pathlib, subprocess
nl = chr(10)
home = pathlib.Path.home()
wc, ws = home/".config/waybar/config.jsonc", home/".config/waybar/style.css"
rc, sc = home/".config/rofi/minimal.rasi", home/".config/swaync/style.css"
hl, osd = home/".config/hypr/hyprland.lua", home/".config/hypr/scripts/osd-popup.py"
top = subprocess.run(["rofi","-dmenu","-i","-theme",str(rc),"-theme-str","window { width: 245px; } mainbox { children: [listview]; } listview { lines: 5; padding: 0px; spacing: 0px; }"],input=nl.join([chr(0xf085)+"  System",chr(0xf1fc)+"  Appearance",chr(0xf03e)+"  Wallpapers",chr(0xf11c)+"  Keybinds",chr(0xf0db)+"  Yazi Cheatsheet"]),text=True,capture_output=True).stdout.strip()
if "Wallpapers" in top: subprocess.Popen(["python3",str(home/".config/waybar/scripts/wallpaper-menu.py")],start_new_session=True)
elif "Keybinds" in top: subprocess.Popen("rofi -dmenu -i -p keys -theme ~/.config/rofi/minimal.rasi -theme-str 'window { width: 720px; }' < ~/.config/hypr/cheatsheet.txt",shell=True,start_new_session=True)
elif "Yazi Cheatsheet" in top: subprocess.Popen("rofi -dmenu -i -p yazi -theme ~/.config/rofi/minimal.rasi -theme-str 'window { width: 720px; }' < ~/.config/hypr/yazi-cheatsheet.txt",shell=True,start_new_session=True)
elif "System" in top:
    sub = subprocess.run(["rofi","-dmenu","-i","-theme",str(rc),"-theme-str","window { width: 260px; } mainbox { children: [listview]; } listview { lines: 2; padding: 0px; spacing: 0px; }"],input=nl.join([chr(0xf0e7)+"  Auto-Boost Apps",chr(0xf2c9)+"  Fan & Thermal GUI"]),text=True,capture_output=True).stdout.strip()
    if "Auto-Boost Apps" in sub: subprocess.Popen([str(home/".config/hypr/scripts/perf-apps-menu.sh")],start_new_session=True)
    elif "Fan & Thermal GUI" in sub: subprocess.Popen(["coolercontrol"],start_new_session=True)
elif "Appearance" in top:
    idx = 0
    while True:
        c, r, s, l, cfg, o = ws.read_text(), rc.read_text(), sc.read_text(), hl.read_text(), wc.read_text(), osd.read_text()
        dm = "Off" if "rgba(255, 255, 255, 0.72)" in c or "background-color: #ffffff;" in c.split("}")[0] else "On"
        ac = "On" if "0.72" in c else "Off"
        ps = next((x.title() for x in ["top","bottom","left","right"] if f'"position": "{x}"' in cfg), "Top")
        ol = "On" if "border_size = 2" in l else "Off"
        rd = "On" if "rounding       = 10" in l else "Off"
        vb_path = "/home/mocha/.config/hypr/shaders/vibrance.glsl"
        vb = "On" if f'screen_shader  = "{vb_path}"' in l else "Off"
        an = "On" if "animations = {\n        enabled = true," in l else "Off"
        bg, fg = ("#000000","#ffffff") if dm=="On" else ("#ffffff","#000000")
        bgr, rfr = ("rgba(0, 0, 0, 0.72)","#000000b8") if dm=="On" else ("rgba(255, 255, 255, 0.72)","#ffffffb8")
        items = [((chr(0xf186) if dm=="On" else chr(0xf185))+"  Dark Mode",dm),(chr(0xf06e)+"  Acrylic",ac),(chr(0xf0c9)+"  Waybar",ps),(chr(0xf065)+"  Outlines",ol),((chr(0xf111) if rd=="On" else chr(0xf096))+"  Rounded",rd),(chr(0xf042)+"  Vibrance",vb),(chr(0xf04b)+"  Animations",an)]
        menu = nl.join(f"{k:<15}{v:>5}" for k, v in items)
        ch = subprocess.run(["rofi","-dmenu","-i","-selected-row",str(idx),"-theme",str(rc),"-theme-str","window { width: 280px; } mainbox { children: [listview]; } listview { lines: 7; padding: 0px; spacing: 0px; }"],input=menu,text=True,capture_output=True).stdout.strip()
        if not ch: break
        idx = ["Dark Mode","Acrylic","Waybar","Outlines","Rounded","Vibrance","Animations"].index(next(x for x in ["Dark Mode","Acrylic","Waybar","Outlines","Rounded","Vibrance","Animations"] if x in ch))
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
            lr = nl.join(["",mark,"hl.layer_rule({ name = 'mocha-waybar-blur', match = { namespace = 'waybar' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-rofi-blur', match = { namespace = 'rofi' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-cc-blur', match = { namespace = 'swaync-control-center' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-win-blur', match = { namespace = 'swaync-notification-window' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-osd-blur', match = { namespace = 'mocha-osd' }, blur = true, ignore_alpha = 0.2 })",""])
            l = next(iter(l.split(nl+mark))) + (lr if on else "")
            o = o.replace(f"background-color: {bg};",f"background-color: {bgr};") if on else o.replace(f"background-color: {bgr};",f"background-color: {bg};")
        elif "Waybar" in ch:
            import json
            order = ["top","bottom","left","right"]
            cur = next((x for x in order if f'"position": "{x}"' in cfg), "top")
            nxt = order[(order.index(cur)+1)%4]
            d = json.loads(cfg)
            vert = nxt in ("left","right")
            d.update({"position":nxt,"height":0 if vert else 30,"width":30 if vert else 0,"margin-top":8 if nxt!="bottom" else 0,"margin-bottom":8 if nxt!="top" else 0,"margin-left":8 if nxt!="right" else 0,"margin-right":8 if nxt!="left" else 0,"modules-center":[] if vert else ["hyprland/window"]})
            d["clock"]["format"] = "{:%I"+nl+"%M}" if vert else "{:%I:%M %p}"
            d["battery"]["format"] = "{icon}" if vert else "{icon} {capacity}%"
            d["wireplumber"]["format"] = "{icon}" if vert else "{icon} {volume}%"
            d["backlight"]["format"] = "{icon}" if vert else "{icon} {percent}%"
            wc.write_text(json.dumps(d,indent=2)+nl)
            vb = nl+"/* mocha-vert */"+nl+"#custom-menu, #clock, #custom-workspaces, #tray, #custom-caffeine, #battery, #wireplumber, #backlight, #bluetooth, #network, #custom-power { padding: 8px 0; min-width: 30px; }"+nl+"/* end-mocha-vert */"
            c = c.split(nl+"/* mocha-vert */")[0] + (vb if vert else "")
            l = l.replace('style = "slide"','style = "slidevert"') if vert else l.replace('style = "slidevert"','style = "slide"')
            hl.write_text(l)
        elif "Outlines" in ch:
            on = ch.endswith("Off")
            l = l.replace("border_size = 0,","border_size = 2,",1) if on else l.replace("border_size = 2,","border_size = 0,",1)
            c = c.replace("border: none; /* mocha-ol */",f"border: 2px solid {fg};") if on else c.replace(f"border: 2px solid {fg};","border: none; /* mocha-ol */")
            s = s.replace("border: none; /* mocha-ol */",f"border: 2px solid {fg};") if on else s.replace(f"border: 2px solid {fg};","border: none; /* mocha-ol */")
            r = r.replace("border: 0px; /* mocha-ol */","border: 2px;").replace("border: 0px; /* mocha-in */","border: 0px 0px 2px 0px;") if on else r.replace("border: 2px;","border: 0px; /* mocha-ol */").replace("border: 0px 0px 2px 0px;","border: 0px; /* mocha-in */")
        elif "Rounded" in ch:
            on = ch.endswith("Off")
            l = l.replace("rounding       = 0,","rounding       = 10,",1) if on else l.replace("rounding       = 10,","rounding       = 0,",1)
            c = c.replace("border-radius: 0;","border-radius: 10px;").replace("border-radius: 0px;","border-radius: 10px;") if on else c.replace("border-radius: 10px;","border-radius: 0;")
            s = s.replace("border-radius: 0px;","border-radius: 10px;") if on else s.replace("border-radius: 10px;","border-radius: 0px;")
            r = r.replace("border-radius: 0px;","border-radius: 10px;") if on else r.replace("border-radius: 10px;","border-radius: 0px;")
        elif "Vibrance" in ch:
            on = ch.endswith("Off")
            l = l.replace("screen_shader  = \"\"", f"screen_shader  = \"{vb_path}\"") if on else l.replace(f"screen_shader  = \"{vb_path}\"", "screen_shader  = \"\"")
        elif "Animations" in ch:
            on = ch.endswith("Off")
            l = l.replace("animations = {\n        enabled = false,","animations = {\n        enabled = true,",1) if on else l.replace("animations = {\n        enabled = true,","animations = {\n        enabled = false,",1)
        if "Dark Mode" not in ch:
            ws.write_text(c); rc.write_text(r); sc.write_text(s); hl.write_text(l); osd.write_text(o)
        subprocess.run(["hyprctl","reload"],stdout=-3,stderr=-3)
        subprocess.run(["swaync-client","-rs"],stdout=-3,stderr=-3)
        subprocess.run(["killall","waybar"],stdout=-3,stderr=-3)
        subprocess.run(["pkill","-f","osd-popup.py"],stdout=-3,stderr=-3)
        subprocess.Popen(["python3",str(osd)],stdout=-3,stderr=-3,start_new_session=True)
        subprocess.Popen(["waybar"],stdout=-3,stderr=-3,start_new_session=True)
