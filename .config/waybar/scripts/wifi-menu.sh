#!/usr/bin/env bash
THEME="$HOME/.config/rofi/minimal.rasi"
PASS_THEME='window { width: 420px; } mainbox { children: [inputbar]; } inputbar { orientation: vertical; children: [prompt, entry]; spacing: 6px; } entry { placeholder: "Input password here"; placeholder-color: #777777; } listview { enabled: false; }'
LIST_THEME='window { width: 640px; } mainbox { children: [listview]; }'
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
list=$(awk -F: 'NR==FNR{saved[$1]=1; next} $2!=""{ssid=$2; if(!seen[ssid]++){prefix=($1=="*"?"* ":"  "); name=prefix ssid; if(length(name)>32) name=substr(name,1,29)"..."; sig=$3"%"; act=(ssid in saved?"Forget":"Connect"); row=sprintf("%-34s %-16s %7s", name, sig, act); if($1=="*") active=row; else rest=(rest?rest "\n":"") row}} END{if(active) print active; if(rest) print rest}' <(nmcli -t -f NAME,TYPE connection show | awk -F: '$2=="802-11-wireless"{print $1}') <(printf "%s\n" "$raw"))
chosen=$(printf "%s\n" "$list" | rofi -dmenu -theme "$THEME" -theme-str "$LIST_THEME")
[ -z "$chosen" ] && exit 0
ssid=$(echo "$chosen" | sed -E 's/^(\* |  )//; s/ +[0-9]+% +(Forget|Connect)$//')
action=$(echo "$chosen" | awk '{print $NF}')
if [ "$action" = "Forget" ]; then
    confirm=$(printf "Yes\nNo\n" | rofi -dmenu -p "Forget $ssid?" -theme "$THEME" -theme-str "$CONFIRM_THEME")
    if [ "$confirm" = "Yes" ]; then
        nmcli connection delete id "$ssid" && rm -f "$CACHE" && notify-send "Wi-Fi" "Forgot $ssid"
    fi
else
    sec=$(printf "%s\n" "$raw" | awk -F: -v s="$ssid" '$2==s{print $4; exit}')
    if [ -z "$sec" ] || [ "$sec" = "--" ]; then
        nmcli device wifi connect "$ssid" && notify-send "Wi-Fi" "Connected to $ssid"
    else
        pass=$(rofi -dmenu -password -p "$ssid" -theme "$THEME" -theme-str "$PASS_THEME")
        [ -z "$pass" ] && exit 0
        nmcli device wifi connect "$ssid" password "$pass" && notify-send "Wi-Fi" "Connected to $ssid" || notify-send "Wi-Fi" "Failed to connect to $ssid"
    fi
fi
