file="$tmpdir"/job-new.json
lava job new "$file"
test -f "$file"
