#!/usr/bin/env bash
DIR="~/Pictures/Screenshots"
mkdir -p "$DIR"
FILE="$DIR/shot_$(date +%Y%m%d_%H%M%S).png"
if [ "$1" = "region" ]; then
  GEOM=$(slurp -b 00000080 -c ffffffff) || exit 0
  grim -g "$GEOM" "$FILE" || exit 1
else
  grim "$FILE" || exit 1
fi
wl-copy < "$FILE"
notify-send -i "$FILE" "Screenshot" "Saved: $(basename "$FILE")" 2>/dev/null
