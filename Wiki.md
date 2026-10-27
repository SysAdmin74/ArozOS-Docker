# Docker environment configuration

This guide covers the Docker wrapper for [tobychui's ArozOS](https://github.com/tobychui/arozos). The application flags and defaults below come from `arozos -help` in the pinned **v2.025** release. `AROZOS_*` variable names are provided by this repository's entrypoint, not by upstream ArozOS itself.

## Requirements and quick start

Use an amd64 (x86-64) Docker host and Docker Compose **2.24.0 or newer**. Run these commands from the repository root:

```sh
cp .env.example .env
# Edit .env before starting.
docker compose up -d --build
docker compose logs --tail=50 app
```

The supplied configuration publishes host port **8980** to container port **8080**. Initial startup extracts the bundled web assets into an empty web volume. It leaves existing assets intact.

The example `.env` contains:

```dotenv
AROZOS_HOSTNAME=My ArozOS Docker
AROZOS_PORT=8080
AROZOS_PUBLIC_REG=false
AROZOS_ENABLE_HWMAN=false
AROZOS_ENABLE_PWMAN=false
```

These are example overrides, not the upstream defaults. Without `.env`, Compose still starts and upstream defaults apply. In particular, upstream hardware and power management default to enabled.

## How variables are applied

A variable such as `AROZOS_PUBLIC_REG=false` becomes the argument `-public_reg=false`.

- Unset variables leave the upstream default unchanged.
- Prefixed variables take precedence over legacy lowercase names, such as `hostname` or `public_reg`.
- An explicitly empty prefixed value is forwarded; it does not restore the default. Empty integers and booleans are invalid upstream values.
- Values containing spaces remain one argument. The entrypoint does not evaluate shell expressions in values.
- Only variables in the reference below are translated. Unknown `AROZOS_*` names are ignored.
- Additional command-line flags follow environment-derived flags and override repeated Go flags.

Use `true` or `false` for booleans. In a Compose `environment` mapping, quote them:

```yaml
environment:
  AROZOS_HOSTNAME: "My Home Server"
  AROZOS_PUBLIC_REG: "false"
```

Compose `environment` entries override the service's `env_file`. This repository explicitly loads `.env` into the container; Compose also reads it for `${...}` interpolation. An exported shell variable can override interpolation without changing the value loaded through `env_file`, so avoid conflicting `AROZOS_PORT` values in your shell and `.env`.

After editing environment settings, recreate the service as needed:

```sh
docker compose up -d
```

`docker compose restart` alone does not apply changed environment values. `.env` is ignored by Git. Do not commit credentials; environment variables and process arguments remain visible to Docker administrators even though the entrypoint does not log arguments.

## HTTP ports and reverse proxies

`AROZOS_PORT` controls the port **inside** the container. The supplied mapping is `8980:${AROZOS_PORT:-8080}`, so setting `AROZOS_PORT=9080` keeps host port 8980 and changes the container target to 9080. To change the host port, edit the left side of the mapping in your Compose configuration.

`AROZOS_HOST` is a bind address; `AROZOS_HOSTNAME` is the display name. Leave the bind address unset or use `0.0.0.0` for access through published ports. Binding to container loopback prevents normal access through Docker port publishing.

Behind a reverse proxy, consider `AROZOS_DISABLE_IP_RESOLVER=true` as described by upstream. Configure the proxy's upstream address, TLS, upload limits, and timeouts separately; the flag does not configure your proxy.

## HTTPS example

Place a certificate and its private key in a directory outside the checkout, then create `compose.tls.yml` in the repository root with the following content. Replace `/absolute/path/to/certificates` with that directory:

```yaml
services:
  app:
    environment:
      AROZOS_TLS: "true"
      AROZOS_TLS_PORT: "8443"
      AROZOS_CERT: /tls/server.crt
      AROZOS_KEY: /tls/server.key
      AROZOS_DISABLE_HTTP: "true"
    volumes:
      - /absolute/path/to/certificates:/tls:ro
    ports:
      - "8443:8443"
```

Apply both files:

```sh
docker compose -f docker-compose.yml -f compose.tls.yml up -d
```

Compose merges this port entry with the base HTTP mapping. With HTTP disabled, the HTTP mapping remains published but has no listening HTTP service. Remove that mapping from your base configuration if you want only the TLS port published. Never set `AROZOS_DISABLE_HTTP=true` without enabling TLS. Certificate paths are container paths; make sure the process can read both mounted files.

Validate with a client that trusts your certificate authority. For a private CA, supply its certificate with curl's `--cacert`; do not disable certificate verification. TLS settings do not automatically change the port mappings.

## Running without Compose

Build and run the image with persistent named volumes:

```sh
docker build -t arozos-local ./container
docker run -d --name arozos --restart unless-stopped \
  --env-file .env \
  -p 8980:8080 \
  -v arozos-files:/arozos/files \
  -v arozos-web:/arozos/web \
  -v arozos-system:/arozos/system \
  arozos-local
```

This example assumes `AROZOS_PORT=8080`. Update the target port if you change it. To supply additional flags, append them after the image name, for example `arozos-local -public_reg=false`. With Compose, use a list such as `command: ["-public_reg=false"]`.

## Persistent storage

| Compose host directory | Container path | Purpose |
| --- | --- | --- |
| `./container/data/files` | `/arozos/files` | User files |
| `./container/data/web` | `/arozos/web` | Web application assets |
| `./container/data/system` | `/arozos/system` | Persistent system data, including accounts and configuration |

The working directory is `/arozos`, so upstream relative paths resolve there. When changing `AROZOS_ROOT`, `AROZOS_STORAGE_CONFIG`, or `AROZOS_TMP`, provide mounts for the new paths as appropriate. A variable does not create a Docker mount. ArozOS creates a `tmp/` directory beneath the `AROZOS_TMP` path.

Stop the service before taking a consistent backup of all three data directories. Container recreation preserves mounted data; deleting host directories or named volumes does not. Keep backups outside the checkout.

`AROZOS_UUID` is intended for initial identity configuration. Changing it may not replace a persisted identity. `AROZOS_SESSION_KEY`, when supplied, must be 16, 24, or 32 bytes; otherwise leave it unset for automatic generation.

## Full variable reference

Descriptions and defaults are from the pinned upstream help output. Boolean flags without an indicated default default to `false`; string flags without an indicated default default to an empty string. `AROZOS_VERSION=true` prints the version and exits rather than starting a server; use it for one-off inspection, not a service with a restart policy.

| Variable | Type | Upstream description/default |
| --- | --- | --- |
| `AROZOS_ALLOW_AUTOLOGIN` | bool | Allow RESTFUL login redirection that allow machines like billboards to login to the system on boot (default true) |
| `AROZOS_ALLOW_CLUSTER` | bool | Enable cluster operations within LAN. Require allow_mdns=true flag (default true) |
| `AROZOS_ALLOW_IOT` | bool | Enable IoT related APIs and scanner. Require MDNS enabled (default true) |
| `AROZOS_ALLOW_MDNS` | bool | Enable MDNS service. Allow device to be scanned by nearby ArOZ Hosts (default true) |
| `AROZOS_ALLOW_PKG_INSTALL` | bool | Allow the system to install package using Advanced Package Tool (aka apt or apt-get) (default true) |
| `AROZOS_ALLOW_SSDP` | bool | Enable SSDP service, disable this if you do not want your device to be scanned by Windows's Network Neighborhood Page (default true) |
| `AROZOS_ALLOW_UPNP` | bool | Enable uPNP service, recommended for host under NAT router |
| `AROZOS_BETA_SCAN` | bool | Allow compatibility to ArOZ Online Beta Clusters |
| `AROZOS_BUFFFILE_SIZE` | int | Maxmium buffer file size (in MB) for buffer required file system abstractions (default 25) |
| `AROZOS_BUFFPOOL_SIZE` | int | Maxmium buffer pool size (in MB) for buffer required file system abstractions (default 1024) |
| `AROZOS_CERT` | string | TLS certificate file (.crt) (default "localhost.crt") |
| `AROZOS_CONSOLE` | bool | Enable the debugging console. |
| `AROZOS_DIR_LIST` | bool | Enable directory listing (default true) |
| `AROZOS_DISABLE_HTTP` | bool | Disable HTTP server, require tls=true |
| `AROZOS_DISABLE_IP_RESOLVER` | bool | Disable IP resolving if the system is running under reverse proxy environment |
| `AROZOS_DISABLE_SUBSERVICE` | bool | Disable subservices completely |
| `AROZOS_ENABLE_BUFFPOOL` | bool | Enable buffer pool for buffer required file system abstractions (default true) |
| `AROZOS_ENABLE_HWMAN` | bool | Enable hardware management functions in system (default true) |
| `AROZOS_ENABLE_PWMAN` | bool | Enable power management of the host system (default true) |
| `AROZOS_FORCE_MAC` | string | Force MAC address to be used for discovery services. If not set, it will use the first NIC |
| `AROZOS_GZIP` | bool | Enable gzip compress on file server (default true) |
| `AROZOS_HOMEPAGE` | bool | Enable user homepage. Accessible via /www/{username}/ (default true) |
| `AROZOS_HOST` | string | Listening host for HTTP server |
| `AROZOS_HOSTNAME` | string | Default name for this host (default "My ArOZ") |
| `AROZOS_IOBUF` | int | Amount of buffer memory for IO operations (default 1024) |
| `AROZOS_KEY` | string | TLS key file (.key) (default "localhost.key") |
| `AROZOS_LOGGING` | bool | Enable logging to file for debug purpose (default true) |
| `AROZOS_MAX_UPLOAD_SIZE` | int | Maxmium upload size in MB. Must not exceed the available ram on your system (default 8192) |
| `AROZOS_NTT` | int | Nightly tasks execution time. Default 3 = 3 am in the morning (default 3) |
| `AROZOS_PORT` | int | Listening port for HTTP server (default 8080) |
| `AROZOS_PUBLIC_REG` | bool | Enable public register interface for account creation |
| `AROZOS_ROOT` | string | User root directories (default "./files/") |
| `AROZOS_SESSION_KEY` | string | Session key, must be 16, 24 or 32 bytes long (AES-128, AES-192 or AES-256). Leave empty for auto generated. |
| `AROZOS_SKIP_MDADM_RELOAD` | bool | Skip mdadm reload config during startup, might result in werid RAID device ID in some Linux distro |
| `AROZOS_STORAGE_CONFIG` | string | File location of the storage config file (default "./system/storage.json") |
| `AROZOS_TLS` | bool | Enable TLS on HTTP serving (HTTPS Mode) |
| `AROZOS_TLS_PORT` | int | Listening port for HTTPS server (default 8443) |
| `AROZOS_TMP` | string | Temporary storage, can be access via tmp:/. A tmp/ folder will be created in this path. Recommend fast storage devices like SSD (default "./") |
| `AROZOS_TMP_TIME` | int | Time before tmp file will be deleted in seconds. Default 86400 seconds = 24 hours (default 86400) |
| `AROZOS_UPLOAD_ASYNC` | bool | Enable file upload buffering to run in async mode (Faster upload, require RAM >= 8GB) |
| `AROZOS_UPLOAD_BUF` | int | Upload buffer memory in MB. Any file larger than this size will be buffered to disk (slower). (default 25) |
| `AROZOS_UUID` | string | System UUID for clustering and distributed computing. Only need to config once for first time startup. Leave empty for auto generation. |
| `AROZOS_VERSION` | bool | Show system build version |
| `AROZOS_WLAN_INTERFACE_NAME` | string | The default wireless interface for connecting to an AP (default "wlan0") |
| `AROZOS_WPA_SUPPLICANT_CONFIG` | string | Path for the wpa_supplicant config (default "/etc/wpa_supplicant/wpa_supplicant.conf") |

## Host-dependent features

Flags alone do not provide devices, utilities, privileges, or network access. Hardware management, power management, Wi-Fi, and RAID require appropriate host support. The example disables hardware and power management; do not enable broad container privileges merely to make a flag work. Samba is not installed in the image.

IoT and cluster discovery depend on mDNS. Docker bridge networking can limit multicast discovery, including mDNS and SSDP. Test these features in your actual network topology; the HTTP/HTTPS checks do not validate them.

Upload and buffer limits should fit the container's memory and temporary disk capacity. Upstream recommends at least 8 GB RAM for asynchronous upload buffering. Raising an application limit does not increase Docker's resource allocation.

## Shutdown and upgrades

ArozOS runs directly as PID 1 so Docker's stop signal reaches its cleanup handler. Docker's restart policy manages restarts. The upstream launcher and its in-place updater are not used.

The Dockerfile pins ArozOS v2.025, checksums for the binary and web archive, and the base image digest. Debian packages still come from live repositories, so builds are not bit-for-bit reproducible. A new upstream release requires an explicit Dockerfile update and validation; rebuilding alone does not select the newest release.

Back up data before upgrading. Review upstream migration requirements and update the binary and web assets together. The entrypoint intentionally does not overwrite populated web volumes, so replacing the image alone does not upgrade existing web assets. Plan a backed-up web-asset migration rather than deleting a volume blindly.

## Troubleshooting and validation

```sh
docker compose ps
docker compose logs --tail=100 app
docker compose config --quiet
python3 -m unittest discover -s tests -v
```

Avoid sharing a full rendered Compose configuration or container inspection output when it contains secrets. For failed startup, check the logs for invalid flag values, certificate paths, or storage permissions. If a variable appears ineffective, check its spelling, precedence, container recreation, and whether the setting initializes persistent state only once.

See [validation results](tests/VALIDATION.md) for the tested TLS, persistence, upload/download, and shutdown behavior. Hardware and LAN discovery remain host-dependent and unverified.
