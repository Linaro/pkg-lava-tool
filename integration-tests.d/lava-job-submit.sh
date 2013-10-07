fixed_response 999

lava_config <<EOF
[DEFAULT]
server = validation.example.com

[server=validation.example.com]
rpc_endpoint = http://localhost:5000/ok
EOF

LAVACACHE="${tmpdir}/config" lava job submit integration-tests.d/sample/nexus.json -n > $tmpdir/output
grep "Job submitted with job ID 999" $tmpdir/output
