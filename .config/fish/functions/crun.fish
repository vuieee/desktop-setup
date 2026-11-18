function crun
    set -l file $argv
    test -z "$file"; and set file (ls -t *.c 2>/dev/null | head -n 1)
    test -z "$file"; and echo "No .c file found"; and return 1
    mkdir -p ~/Projects/c/bin
    set -l out "$HOME/Projects/c/bin/"(basename "$file" .c)
    gcc -Wall -Wextra -std=c17 "$file" -o "$out" -lm; and "$out"
end
