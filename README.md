# Coriolis Metal Hub Python Client

`coriolis-metal-hub` is a command-line and Python client for the Coriolis Metal
Hub deployment. It manages registered bare-metal servers through the hub and creates,
lists, inspects, and deletes snapshots on those servers.

The client connects to the hub with mutual TLS. By default, hub requests are
authenticated through OpenStack Keystone.

## Requirements

- Python 3
- Network access to the Coriolis Metal Hub API and the registered server agents
- Paths to a CA certificate, a client certificate, and its private key
- Keystone credentials (or a token) when the hub requires Keystone authentication

## Installation

Install from a checkout:

```bash
git clone https://github.com/cloudbase/python-coriolismetalhubclient.git
cd python-coriolismetalhubclient
python3 -m pip install .
```

For development, install the checkout in editable mode:

```bash
python3 -m pip install -e .
```

This provides the `coriolis-metal-hub` command.

## Configuration

The command accepts options directly or reads the following environment
variables. Keeping credentials in environment variables avoids repeating them
on every command.

```bash
export CORIOLIS_METAL_ENDPOINT="https://metal-hub.example.com"
export CORIOLIS_METAL_CA_CERT=/path/to/ca.pem
export CORIOLIS_METAL_CLIENT_CERT=/path/to/client-cert.pem
export CORIOLIS_METAL_CLIENT_KEY=/path/to/client-key.pem

export OS_AUTH_URL="https://keystone.example.com/v3"
export OS_USERNAME=metal-user
export OS_PASSWORD='replace-with-a-secret'
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=metal-project
export OS_PROJECT_DOMAIN_NAME=Default
```

For Keystone v3, supply one of the following project scopes:

- `OS_PROJECT_ID`
- `OS_PROJECT_NAME` together with `OS_PROJECT_DOMAIN_NAME`
- `OS_PROJECT_NAME` together with `OS_PROJECT_DOMAIN_ID`

For a token-based login, set `OS_AUTH_URL`, `OS_AUTH_TOKEN`, and an appropriate
project scope instead of username/password. Keystone v2 is supported by setting
`OS_IDENTITY_API_VERSION` to `2` or `2.0` and providing `OS_TENANT_ID` or
`OS_TENANT_NAME`.

All of these settings can be supplied as command options too. Run
`coriolis-metal-hub --help` for the complete list.

## CLI usage

Commands use the form:

```bash
coriolis-metal-hub [global options] <resource> <action> [arguments]
```

### Server management

```bash
# List servers registered with the hub
coriolis-metal-hub server list

# Show one server
coriolis-metal-hub server show <server-id>

# Register a server agent endpoint
coriolis-metal-hub server add https://metal-agent.example.com

# Change an existing server agent endpoint
coriolis-metal-hub server update <server-id> \
  --api-endpoint https://new-metal-agent.example.com

# Ask the hub to refresh server metadata
coriolis-metal-hub server refresh <server-id>

# Remove a server from the hub
coriolis-metal-hub server remove <server-id>
```

### Snapshot management

Snapshot operations address a server by its hub server ID. Creating a snapshot
without selecting disks snapshots all disks reported by that server agent.

```bash
# List a server's snapshots
coriolis-metal-hub snapshot list <server-id>

# Create a snapshot of all disks on a server
coriolis-metal-hub snapshot create <server-id>

# Inspect a snapshot
coriolis-metal-hub snapshot show <server-id> <snapshot-id>

# Delete a snapshot
coriolis-metal-hub snapshot delete <server-id> <snapshot-id>
```

Use command-specific help for argument details:

```bash
coriolis-metal-hub server add --help
coriolis-metal-hub snapshot create --help
```

## Python API

The package also exposes `HubClient` for hub operations and `AgentClient` for
operations performed directly against a registered agent. The hub client needs a
Keystone session when authentication is enabled.

```python
from coriolismetalhub.client import HubClient

client_certs = {
    "cert": "/path/to/client-cert.pem",
    "key": "/path/to/client-key.pem",
    "ca": "/path/to/ca.pem",
}

# Create ks_session with keystoneauth1, then:
hub = HubClient(
    endpoint="https://metal-hub.example.com",
    client_certs=client_certs,
    ks_session=ks_session,
)

servers = hub.list_servers()
agent = hub.get_client_for_server(servers[0]["id"])
snapshot = agent.create_snapshot()
```

`HubClient` provides `list_servers`, `get_server`, `add_server`,
`update_server`, `refresh_server`, and `remove_server`. An `AgentClient` provides
disk and snapstore discovery plus snapshot creation, inspection, deletion,
change lookup, and range-based snapshot downloads.

## License

Apache License 2.0. See [LICENSE](LICENSE).
