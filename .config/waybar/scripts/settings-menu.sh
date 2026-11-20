#!/usr/bin/env python3
import os, pathlib, subprocess, time
try: os.setsid()
except Exception: pass
nl = chr(6)
home = pathlib.Path.home()
wc, ws = home/".config/waybar/config.jsonc", home/".config/waybar/style.css"
rc, sc = home/".config/rofi/minimal.rasi", home/".config/swaync/style.css"
hl, osd = home/".config/hypr/hyprland.lua", home/".config/hypr/scripts/osd-popup.py"
top = subprocess.run(["rofi","-dmenu","-i","-theme",str(rc),"-theme-str","window { width: 245px; } mainbox { children: [listview]; } listview { lines: 6; padding: 0px; spacing: 0px; }"],input=nl.join([chr(0xf085)+"  System",chr(0xf1fc)+"  Appearance",chr(0xf68)+"  Display",chr(0xf03e)+"  Wallpapers",chr(0xf11c)+"  Keybinds",chr(0xf0db)+"  Yazi Cheatsheet"]),text=True,capture_output=True).stdout.strip()
if "Display" in top: subprocess.Popen(["python3",str(home/".config/waybar/scripts/display-menu.py")],start_new_session=True)
elif "Wallpapers" in top: subprocess.Popen(["python3",str(home/".config/waybar/scripts/wallpaper-menu.py")],start_new_session=True)
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
        th = "Default" if (home/".local/share/mocha-theme-bak/native").exists() else "Mono"
        dm = "Off" if any(x in c for x in ("rgba(255, 255, 255, 0.72)", "background-color: #ffffff;", "rgba(248, 250, 252, 0.78)", "background-color: #f8fafc;")) else "On"
        ac = "On" if ("0.72" in c or "0.75" in c) else "Off"
        ps = next((x.title() for x in ["top","bottom"] if f'"position": "{x}"' in cfg), "Top")
        ol = "On" if ("border_size = 2" in l or "border_size = 1" in l) else "Off"
        rd = "On" if "rounding       = 6" in l else "Off"
        vb_path = "/home/mocha/.config/hypr/shaders/vibrance.glsl"
        vb = "On" if f'screen_shader  = "{vb_path}"' in l else "Off"
        an = "On" if "animations = {\n        enabled = true," in l else "Off"
        bg, fg = (("#111318","#f1f5f9") if th=="Default" else ("#000000","#ffffff")) if dm=="On" else (("#f8fafc","#0f172a") if th=="Default" else ("#ffffff","#000000"))
        bd = ("#64748b" if dm=="On" else "#94a3b8") if th=="Default" else fg
        bgr, rfr = (("rgba(17, 19, 24, 0.78)","#111318bf") if th=="Default" else ("rgba(0, 0, 0, 0.72)","#000000b8")) if dm=="On" else (("rgba(248, 250, 252, 0.78)","#f8fafcbf") if th=="Default" else ("rgba(255, 255, 255, 0.72)","#ffffffb8"))
        items = [((chr(0xf186) if dm=="On" else chr(0xf185))+"  Dark Mode",dm),(chr(0xf06e)+"  Acrylic",ac),(chr(0xf0c9)+"  Waybar",ps),(chr(0xf065)+"  Outlines",ol),((chr(0xf111) if rd=="On" else chr(0xf096))+"  Rounded",rd),(chr(0xf042)+"  Vibrance",vb),(chr(0xf04b)+"  Animations",an),(chr(0xf1fc)+"  Theme",th)]
        menu = nl.join(f"{k:<15}{v:>5}" for k, v in items)
        ch = subprocess.run(["rofi","-dmenu","-i","-selected-row",str(idx),"-theme",str(rc),"-theme-str","window { width: 280px; } mainbox { children: [listview]; } listview { lines: 8; padding: 0px; spacing: 0px; }"],input=menu,text=True,capture_output=True).stdout.strip()
        if not ch: break
        idx = ["Dark Mode","Acrylic","Waybar","Outlines","Rounded","Vibrance","Animations","Theme"].index(next(x for x in ["Dark Mode","Acrylic","Waybar","Outlines","Rounded","Vibrance","Animations","Theme"] if x in ch))
        if "Dark Mode" in ch:
            subprocess.run(["python3",str(home/".config/waybar/scripts/toggle-dark.py")])
        elif "Acrylic" in ch:
            on = ch.endswith("Off")
            c = c.replace(f"background-color: {bg};",f"background-color: {bgr};") if on else c.replace(f"background-color: {bgr};",f"background-color: {bg};")
            r=r.replace("* {"+nl+f"    background-color: {bg};","* {"+nl+"    background-color: transparent;").replace("window {"+nl+"    width: 480px;","window {"+nl+f"    background-color: {rfr};{nl}    width: 480px;").replace(f"    background-color: {bg};{nl}    text-color: {fg};","    background-color: transparent;"+nl+f"    text-color: {fg};") if on else r.replace("* {"+nl+"    background-color: transparent;","* {"+nl+f"    background-color: {bg};").replace("window {"+nl+f"    background-color: {rfr};{nl}    width: 480px;","window {"+nl+"    width: 480px;").replace("    background-color: transparent;"+nl+f"    text-color: {fg};",f"    background-color: {bg};{nl}    text-color: {fg};")
            s=s.replace(f"background: {bg};",f"background: {bgr};").replace(".notification {"+nl+f"  background: {bgr};",".notification {"+nl+"  background: transparent;") if on else s.replace(f"background: {bgr};",f"background: {bg};").replace(".notification {"+nl+"  background: transparent;",".notification {"+nl+f"  background: {bg};")
            l = l.replace("active_opacity   = 1.0","active_opacity   = 0.85").replace("inactive_opacity = 1.0","inactive_opacity = 0.78") if on else l.replace("active_opacity   = 0.85","active_opacity   = 1.0").replace("inactive_opacity = 0.78","inactive_opacity = 1.0")
            mark = "-- mocha-acrylic-layers"
            lr = nl.join(["",mark,"hl.layer_rule({ name = 'mocha-waybar-blur', match = { namespace = 'waybar' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-rofi-blur', match = { namespace = 'rofi' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-cc-blur', match = { namespace = 'swaync-control-center' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-swaync-win-blur', match = { namespace = 'swaync-notification-window' }, blur = true, ignore_alpha = 0.2 })","hl.layer_rule({ name = 'mocha-osd-blur', match = { namespace = 'mocha-osd' }, blur = true, ignore_alpha = 0.2 })",""])
            l = next(iter(l.split(nl+mark))) + (lr if on else nl+"hl.layer_rule({ name = 'mocha-waybar-noblur', match = { namespace = 'waybar' }, blur = false })"+nl)
            o = o.replace(f"background-color: {bg};",f"background-color: {bgr};") if on else o.replace(f"background-color: {bgr};",f"background-color: {bg};")
        elif "Waybar" in ch:
            import json, re
            cur = "bottom" if '"position": "bottom"' in cfg else "top"
            nxt = "bottom" if cur == "top" else "top"
            d = json.loads(re.sub(r"//.*", "", cfg))
            d.pop("width", None)
            d.update({"position": nxt, "height": 30, "margin-top": 8 if nxt == "top" else 1, "margin-bottom": 1 if nxt == "top" else 8, "margin-left": 8, "margin-right": 8, "modules-center": ["hyprland/window"]})
            d["clock"]["format"] = "{:%I:%M %p}"
            d["bluetooth"]["format-connected"] = " {device_alias}"
            wc.write_text(json.dumps(d, indent=2) + nl)
        elif "Outlines" in ch:
            on = ch.endswith("Off")
            bw = "1" if th=="Default" else "2"; l = l.replace("border_size = 0,",f"border_size = {bw},",1) if on else l.replace(f"border_size = {bw},","border_size = 0,",1)
            c = c.replace("border: none; /* mocha-ol */",f"border: {bw}px solid {bd};") if on else c.replace(f"border: {bw}px solid {bd};","border: none; /* mocha-ol */")
            s = s.replace("border: none; /* mocha-ol */",f"border: {bw}px solid {bd};") if on else s.replace(f"border: {bw}px solid {bd};","border: none; /* mocha-ol */")
            r = r.replace("border: 0px; /* mocha-ol */",f"border: {bw}px;").replace("border: 0px; /* mocha-in */","border: 0px 0px 2px 0px;") if on else r.replace(f"border: {bw}px;","border: 0px; /* mocha-ol */").replace("border: 0px 0px 2px 0px;","border: 0px; /* mocha-in */")
        elif "Rounded" in ch:
            on = ch.endswith("Off")
            l = l.replace("rounding       = 0,","rounding       = 6,",1) if on else l.replace("rounding       = 6,","rounding       = 0,",1)
            c = c.replace("border-radius: 0;","border-radius: 6px;").replace("border-radius: 0px;","border-radius: 6px;") if on else c.replace("border-radius: 6px;","border-radius: 0;")
            s = s.replace("border-radius: 0px;","border-radius: 6px;") if on else s.replace("border-radius: 6px;","border-radius: 0px;")
            r = r.replace("border-radius: 0px;","border-radius: 6px;",1) if on else r.replace("border-radius: 6px;","border-radius: 0px;",1)
        elif "Vibrance" in ch:
            on = ch.endswith("Off")
            l = l.replace("screen_shader  = \"\"", f"screen_shader  = \"{vb_path}\"") if on else l.replace(f"screen_shader  = \"{vb_path}\"", "screen_shader  = \"\"")
        elif "Theme" in ch:
            subprocess.run(["python3",str(home/".config/waybar/scripts/toggle-theme.py")])
        elif "Animations" in ch:
            on = ch.endswith("Off")
            l = l.replace("animations = {\n        enabled = false,","animations = {\n        enabled = true,",1) if on else l.replace("animations = {\n        enabled = true,","animations = {\n        enabled = false,",1)
        if "Dark Mode" not in ch and "Theme" not in ch:
            ws.write_text(c); rc.write_text(r); sc.write_text(s); hl.write_text(l); osd.write_text(o)
        if "Waybar" in ch:
            subprocess.run(["pkill","-x","waybar"],stdout=-3,stderr=-3)
            time.sleep(0.15)
            subprocess.Popen(["waybar"],stdout=-3,stderr=-3,start_new_session=True)
            continue
        subprocess.run(["hyprctl","reload"],stdout=-3,stderr=-3)
        subprocess.run(["swaync-client","-rs"],stdout=-3,stderr=-3)
        subprocess.run(["pkill","-x","waybar"],stdout=-3,stderr=-3)
        subprocess.run(["pkill","-f","osd-popup.py"],stdout=-3,stderr=-3)
        time.sleep(0.15)
        subprocess.Popen(["python3",str(osd)],stdout=-3,stderr=-3,start_new_session=True)
        subprocess.Popen(["waybar"],stdout=-3,stderr=-3,start_new_session=True)
