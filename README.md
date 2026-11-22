# desktop-setup

[![Desktop Preview](preview/desktop.png?raw=true)](preview/desktop.png?raw=true)

> [!IMPORTANT]
> ## Disclaimer
>
> Please read this before you copy anything into your home directory.
>
> **1. Stability.** Most of the user interface and usability of these configs is stable and responsive. Some portions are still broken, and development is slow because I am the only one maintaining this.
>
> **2. Scripts break.** Whenever a new feature is added, or a current one is changed, some of the scripts occasionally break. I fix them when I notice, but expect rough edges after any big change.
>
> **3. This is not HyDE or dusky.** This is not a full dotfiles distribution like [HyDE](https://github.com/HyDE-Project/HyDE) or [dusky](https://github.com/dusklinux/dusky). There is no guided installer, no theme ecosystem and no support team. If you want a polished, community-maintained experience, use one of those instead.
>
> **4. It's my preference.** This is just my own set of preferences, made to also be somewhat usable for anyone who wants to try my setup. You may not agree with my distro of choice (CachyOS) or my default apps, such as Yazi as the file manager, and that is your right. Swap them out for whatever you like.

My personal desktop configuration for **CachyOS** (Arch-based) running **Hyprland**. It is built around a minimal, hand-made setup: Hyprland, Waybar and Rofi, plus a handful of custom scripts and small GTK overlays instead of a prebuilt rice.

## Included

### Desktop

- **WM:** Hyprland (`hyprland.lua`) with custom GTK3 layer-shell OSD and Power/Lock overlays.
- **Bar:** Waybar with live Dark/Light mode, Mono/Candy theme, Acrylic blur, Outlines, and Rounded and Position toggles.
- **Launcher & Menus:** Rofi (`Alt + Space` settings menu, `Super + Space` app launcher, `Super + V` pinned clipboard manager).
- **Notifications:** SwayNC.

### Apps & Tools

- **File Manager & Terminal:** Kitty + Yazi (`Super + E` and xdg-desktop-portal modal picker) + Fastfetch.
- **C Development (`C Studio`):** Kitty + Micro with `clangd` LSP autocomplete, C snippets, `F5` floating `c-runner` compile and run, and `cnew`/`crun` Fish helpers.
- **Visualizers:** Cava, Unimatrix (`matrix`) and `pipes.sh` (`pipes`).

### Audio & Bluetooth

- **Audio & Bluetooth:** PipeWire + `wiremix` TUI and `bluetui` TUI (with live Bluetooth battery tooltips).
- **Audio Presets:** EasyEffects, see [Audio Presets](#audio-presets-easyeffects) below.

### Power & Thermal

- **Auto-Switch:** AC/battery auto-switching (`165Hz` Balanced on AC, `60Hz` Power Saver on battery).
- **Game Boost:** per-game `performance` profile boost via `game-watcher.py`.

## Quick Install

> [!WARNING]
> This copies files straight into `~/.config` and will overwrite configs with the same name. Back up your existing configs first, for example `cp -r ~/.config ~/.config.bak`.

```
cp -r .config/* ~/.config/
cp -r .local/share/applications/* ~/.local/share/applications/
mkdir -p ~/Pictures/Wallpapers && cp -r Pictures/Wallpapers/* ~/Pictures/Wallpapers/
hyprctl reload
```

The configs expect the apps listed under [Included](#included) to be installed. Missing packages are the most common reason something does not work, so check there first. If something is still broken, see [Known issues](#known-issues).

## Audio Presets (EasyEffects)

- Headless background service (`easyeffects --gapplication-service`, zero tray icon) with a centered floating GUI (`960x640`).
- Presets are sourced from [JackHack96/EasyEffects-Presets](https://github.com/JackHack96/EasyEffects-Presets). See also [speaker-tuning-to-easyeffects](https://github.com/REPLACE-ME/speaker-tuning-to-easyeffects) for OEM speaker extraction.

## Known issues

- Some scripts and menus are broken or half-finished.
- Adding or changing a feature can break an existing script. If something that worked yesterday stops working after an update, that is probably why.
- I only test this on my own machine, so a fresh install on different hardware has not been validated.

Development is slow since it is just me. Issues are welcome, but I can't promise a quick fix.

## Layout

```
.config/             Hyprland, Waybar, Rofi, Kitty, Yazi and other app configs
.local/              desktop entries and local scripts
Pictures/Wallpapers/ wallpapers
browser/             browser-related files
preview/             screenshots used in this README
```

## Credits

- [HyDE](https://github.com/HyDE-Project/HyDE) and [dusky](https://github.com/dusklinux/dusky) for the inspiration, even though this isn't a distribution like them.
- [JackHack96/EasyEffects-Presets](https://github.com/JackHack96/EasyEffects-Presets) for the audio presets.
