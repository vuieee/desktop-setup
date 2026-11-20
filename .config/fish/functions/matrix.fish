function matrix --description "Theme-aware unimatrix"
    if test -e ~/.local/share/mocha-theme-bak/native
        unimatrix -s 96 -l o $argv
    else if grep -q "background-color: #ffffff;\|rgba(255, 255, 255, 0.72)" ~/.config/waybar/style.css 2>/dev/null
        unimatrix -s 96 -c black -l o $argv
    else
        unimatrix -s 96 -c white -l o $argv
    end
end
