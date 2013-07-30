fixed_response 999

lava_config <<CONFIG
[DEFAULT]
server = http://localhost:5000

[server=validation.example.com]
rpc_endpoint = /ok
CONFIG

lava job submit integration-tests.d/sample/nexus.json > $tmpdir/output
grep "Job submitted with job ID 999" $tmpdir/output
