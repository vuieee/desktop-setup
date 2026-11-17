#!/usr/bin/env bash
THEME="$HOME/.config/rofi/minimal.rasi"
PASS_THEME='window { width: 420px; } mainbox { children: [inputbar]; } inputbar { orientation: vertical; children: [prompt, entry]; spacing: 6px; } entry { placeholder: "Input password here"; placeholder-color: #777777; } listview { enabled: false; }'
CONFIRM_THEME='window { width: 360px; } mainbox { children: [inputbar, listview]; } inputbar { children: [prompt]; } entry { enabled: false; } listview { lines: 2; }'
CACHE="/tmp/wifi-scan.cache"
raw=$(nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list --rescan no)
if [ $(printf "%s\n" "$raw" | grep -c .) -gt 1 ]; then
    printf "%s\n" "$raw" > "$CACHE"
elif [ -s "$CACHE" ]; then
    active_ssid=$(printf "%s\n" "$raw" | awk -F: '$1=="*"{print $2; exit}')
    raw=$(awk -F: -v a="$active_ssid" 'BEGIN{OFS=":"} {$1=($2==a?"*":" "); print}' "$CACHE")
fi
(nmcli device wifi rescan >/dev/null 2>&1 && nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list --rescan no > "$CACHE.tmp" && [ $(grep -c . "$CACHE.tmp") -gt 1 ] && mv "$CACHE.tmp" "$CACHE" &)
mapfile -t rows < <(awk -F: 'NR==FNR{saved[$1]=1; next} $2!=""{ssid=$2; if(!seen[ssid]++){prefix=($1=="*"?"* ":"  "); name=prefix ssid; if(length(name)>34) name=substr(name,1,31)"..."; tag=(ssid in saved?"[Saved]":""); label=sprintf("%-36s %-10s %4s%%", name, tag, $3); status=(ssid in saved?"saved":"new"); line=ssid "\t" status "\t" label; if($1=="*") active=line; else rest[++n]=line}} END{if(active) print active; for(i=1;i<=n;i++) print rest[i]}' <(nmcli -t -f NAME,TYPE connection show | awk -F: '$2=="802-11-wireless"{print $1}') <(printf "%s\n" "$raw"))
[ ${#rows[@]} -eq 0 ] && exit 0

menu_items=()
for r in "${rows[@]}"; do
    IFS=$'\t' read -r s st lbl <<< "$r"
    menu_items+=("$lbl")
done

vis_lines=${#rows[@]}
[ "$vis_lines" -gt 8 ] && vis_lines=8
LIST_THEME="window { width: 640px; } mainbox { children: [listview, textbox-hint]; } listview { lines: $vis_lines; } textbox-hint { expand: false; padding: 10px 14px; border: 2px 0px 0px 0px; border-color: #ffffff; text-color: #ffffff; content: \"Enter: Connect   |   F: Forget (Saved)\"; }"

sel=0
while true; do
    out=$(printf "%s\n" "${menu_items[@]}" | rofi -dmenu -format i -selected-row "$sel" -kb-custom-1 "f" -kb-custom-2 "F" -theme "$THEME" -theme-str "$LIST_THEME")
    rc=$?
    [ $rc -eq 1 ] && exit 0
    [ -z "$out" ] && exit 0
    sel="$out"

    IFS=$'\t' read -r ssid status label <<< "${rows[$sel]}"
    [ -z "$ssid" ] && exit 0

    if [ $rc -eq 10 ] || [ $rc -eq 11 ]; then
        if [ "$status" != "saved" ]; then
            notify-send "Wi-Fi" "$ssid is not a saved network"
            continue
        fi
        confirm=$(printf "Yes\nNo\n" | rofi -dmenu -p "Forget $ssid?" -theme "$THEME" -theme-str "$CONFIRM_THEME")
        if [ "$confirm" = "Yes" ]; then
            nmcli connection delete id "$ssid" && rm -f "$CACHE" && notify-send "Wi-Fi" "Forgot $ssid"
            exit 0
        fi
        continue
    fi

    if [ "$status" = "saved" ]; then
        nmcli connection up id "$ssid" && notify-send "Wi-Fi" "Connected to $ssid" || notify-send "Wi-Fi" "Failed to connect to $ssid"
        exit 0
    else
        sec=$(printf "%s\n" "$raw" | awk -F: -v s="$ssid" '$2==s{print $4; exit}')
        if [ -z "$sec" ] || [ "$sec" = "--" ]; then
            nmcli device wifi connect "$ssid" && notify-send "Wi-Fi" "Connected to $ssid"
            exit 0
        else
            pass=$(rofi -dmenu -password -p "$ssid" -theme "$THEME" -theme-str "$PASS_THEME")
            [ -z "$pass" ] && continue
            nmcli device wifi connect "$ssid" password "$pass" && notify-send "Wi-Fi" "Connected to $ssid" || notify-send "Wi-Fi" "Failed to connect to $ssid"
            exit 0
        fi
    fi
done
