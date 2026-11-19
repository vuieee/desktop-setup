#!/usr/bin/env bash
case "$1" in
  vol-up)   wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+ ;;
  vol-down) wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%- ;;
  vol-mute) wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle ;;
  mic-mute) wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle ;;
  bri-up)   brightnessctl set 5%+ >/dev/null ;;
  bri-down) brightnessctl set 5%- >/dev/null ;;
esac
if [ "$1" = "vol-mute" ]; then
  info=$(wpctl get-volume @DEFAULT_AUDIO_SINK@)
  if [[ "$info" == *"[MUTED]"* ]]; then
    icon=""; val="Mute"
  else
    icon=""; val="Unmute"
  fi
elif [ "$1" = "mic-mute" ]; then
  info=$(wpctl get-volume @DEFAULT_AUDIO_SOURCE@)
  if [[ "$info" == *"[MUTED]"* ]]; then
    icon=""; val="Mic Off"
  else
    icon=""; val="Mic On"
  fi
elif [ "$1" = "caps" ]; then
  sleep 0.05
  state=$(cat /sys/class/leds/*capslock*/brightness 2>/dev/null | head -n1)
  if [ "$state" = "1" ]; then
    icon=""; val="Caps On"
  else
    icon=""; val="Caps Off"
  fi
elif [[ "$1" == vol-* ]]; then
  info=$(wpctl get-volume @DEFAULT_AUDIO_SINK@)
  val=$(awk '{printf "%d", $2*100}' <<< "$info")
  sink_info=$(wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null; pactl list sinks 2>/dev/null | grep -A 25 "Name: $(pactl get-default-sink 2>/dev/null)")
  if grep -qiE "headphone|headset|earbud|earphone|airpods|buds|bluez|a2dp" <<< "$sink_info"; then
    icon="Headphones"
  else
    icon="Volume"
  fi
else
  cur=$(brightnessctl g); max=$(brightnessctl m)
  val=$(( cur * 100 / max ))
  icon="Brightness"
fi
python3 /home/mocha/.config/hypr/scripts/osd-popup.py "$icon" "$val" >/dev/null 2>&1 &
