cat > "${tmpdir}/config" <<EOF
[DEFAULT]
device_type = panda

[device_type=panda]
image = file:///path/to/panda.img
EOF
LAVACACHE="${tmpdir}/config" lava job new "${tmpdir}/job.json" -n
cat "${tmpdir}/job.json"
grep "device_type.*panda" "${tmpdir}/job.json" && grep "image.*path.to.panda.img" "${tmpdir}/job.json"
