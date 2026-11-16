#!/bin/sh
# Power menu: a small vertical Rofi list dropping down from the top-right corner.

choice=$(printf 'Lock\nReboot\nFast reboot\nShutdown\n' | rofi -dmenu -i -no-custom \
  -theme ~/.config/rofi/minimal.rasi \
  -theme-str 'window { location: north east; anchor: north east; width: 200px; x-offset: -4px; y-offset: 34px; }' \
  -theme-str 'inputbar { enabled: false; }' \
  -theme-str 'listview { lines: 4; padding: 0px; }' \
  -theme-str 'element { padding: 10px 14px; }')

case "$choice" in
  "Lock")        hyprlock ;;
  "Reboot")      systemctl reboot ;;
  "Fast reboot") systemctl soft-reboot ;;
  "Shutdown")    systemctl poweroff ;;
esac
