# desktop-setup

![Desktop Preview](preview/desktop.png?raw=true)

## Components
- **WM:** Hyprland (`hyprland.lua`) with custom GTK3 layer-shell OSD & Power/Lock overlays
- **Bar:** Waybar with live Dark/Light mode, Mono/Native theme, Acrylic blur, Outlines, Rounded & Position toggles
- **Launcher & Menus:** Rofi (`Alt + Space` settings menu, `Super + Space` app launcher, `Super + V` pinned clipboard manager)
- **Audio & Bluetooth:** PipeWire + `wiremix` TUI & `bluetui` TUI (with live Bluetooth battery tooltips)
- **File Manager & Terminal:** Kitty + Yazi (`Super + E` & xdg-desktop-portal modal picker) + Fastfetch
- **C Development (`C Studio`):** Kitty + Micro (`clangd` LSP autocomplete, C snippets, `F5` floating `c-runner` compile & run, `cnew`/`crun` Fish helpers)
- **Power & Thermal Auto-Switch:** AC/battery auto-switching (`165Hz` Balanced on AC, `60Hz` Power Saver on battery) + per-game `performance` profile boost via `game-watcher.py`
- **Notifications:** SwayNC
- **Visualizers:** Cava, Unimatrix (`matrix`), and `pipes.sh` (`pipes`)

## Quick Install
```bash
cp -r .config/* ~/.config/
cp -r .local/share/applications/* ~/.local/share/applications/
mkdir -p ~/Pictures/Wallpapers && cp -r Pictures/Wallpapers/* ~/Pictures/Wallpapers/
hyprctl reload
```
