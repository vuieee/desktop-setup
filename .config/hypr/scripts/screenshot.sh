#!/usr/bin/env bash
DIR="/home/mocha/Pictures/Screenshots"
mkdir -p "$DIR"
if [ "$1" = "ocr" ]; then
  GEOM=$(slurp -b 00000080 -c ffffffff) || exit 0
  TXT=$(grim -g "$GEOM" - | tesseract stdin stdout --oem 1 -l eng 2>/dev/null | sed "s/[[:space:]]*$//")
  if [ -n "$TXT" ]; then
    printf "%s" "$TXT" | wl-copy
    PREV=$(printf "%s" "$TXT" | tr "
" " " | cut -c1-80)
    notify-send "OCR Copied" "$PREV" 2>/dev/null
  else
    notify-send "OCR" "No text detected" 2>/dev/null
  fi
  exit 0
fi
FILE="$DIR/shot_$(date +%Y%m%d_%H%M%S).png"
if [ "$1" = "region" ]; then
  GEOM=$(slurp -b 00000080 -c ffffffff) || exit 0
  grim -g "$GEOM" "$FILE" || exit 1
else
  grim "$FILE" || exit 1
fi
wl-copy -t image/png < "$FILE"
notify-send -i "$FILE" "Screenshot" "Saved: $(basename "$FILE")" 2>/dev/null
