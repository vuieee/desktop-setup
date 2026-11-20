function pipes --description "Theme-aware pipes.sh"
    if test -e ~/.local/share/mocha-theme-bak/native
        pipes.sh -c 1 -c 2 -c 3 -c 4 -c 5 -c 6 $argv
    else if grep -q "background-color: #ffffff;\|rgba(255, 255, 255, 0.72)" ~/.config/waybar/style.css 2>/dev/null
        pipes.sh -c 0 $argv
    else
        pipes.sh -c 7 $argv
    end
end
