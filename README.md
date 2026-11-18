# desktop-setup

![Desktop Preview](preview/desktop.png?raw=true)

## Components
- **WM:** Hyprland (`hyprland.lua`) with custom GTK3 layer-shell OSD & Power/Lock overlays
- **Bar:** Waybar with live Dark/Light mode, Mono/Native theme, Acrylic blur, Outlines, Rounded & Position toggles
- **Launcher & Menus:** Rofi (`Alt + Space` settings menu, `Super + Space` app launcher, `Super + V` pinned clipboard manager)
- **Audio & Bluetooth:** PipeWire + `wiremix` TUI & `bluetui` TUI (with live Bluetooth battery tooltips)
- **File Manager & Terminal:** Kitty + Yazi (`Super + E` & xdg-desktop-portal modal picker) + Fastfetch
- **Notifications:** SwayNC
- **Visualizers:** Cava, Unimatrix (`matrix`), and `pipes.sh` (`pipes`)

## Quick Install
```bash
cp -r .config/* ~/.config/
cp -r .local/share/applications/* ~/.local/share/applications/
cp Pictures/wallpaper.png ~/Pictures/wallpaper.png
hyprctl reload
```
