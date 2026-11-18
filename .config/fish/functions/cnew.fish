function cnew
    set -l dir ~/Projects/c
    mkdir -p $dir/bin
    set -l name (string replace -r .c$ "" -- $argv)
    test -z "$name"; and set name scratch
    set -l file "$dir/$name.c" 
    if not test -f "$file"
        printf "#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n" > "$file"
    end
    cd $dir; and micro "$file"
end
