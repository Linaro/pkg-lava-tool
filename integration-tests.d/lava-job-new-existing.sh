touch "${tmpdir}/foo.json"
lava job new "${tmpdir}/foo.json"
rc="$?"
test "$rc" -gt 0

