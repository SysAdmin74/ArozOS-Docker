# Container validation

Validated against ArozOS v2.025 on Linux amd64, 2026-10-27.

- Five entrypoint unit tests passed.
- Compose configuration and image build passed. BuildKit verified the pinned release artifact SHA-256 checksums.
- HTTP on container port 9080 and HTTPS on 9443 returned the system-information API.
- HTTPS used a temporary certificate with localhost SANs and explicit CA trust; TLS verification was not disabled.
- Created a temporary administrator through `/system/auth/register`, authenticated through `/system/auth/login`, uploaded a text file through `/system/file_system/upload`, and downloaded matching bytes through `/media/`.
- Removed and recreated the container with the same files/web/system volumes. Fresh login and byte-for-byte download succeeded.
- Recreated with `AROZOS_DISABLE_HTTP=true`; HTTPS worked and the published HTTP port refused/reset connections.
- Docker stop reached the application's database cleanup handler and exited with code 0 in under one second, before and after recreation.

These integration checks used isolated disposable volumes, an ephemeral password, and local-only published ports. They do not certify hardware, multicast discovery, or other host-dependent features. The previous launcher-based entrypoint exited without application cleanup; the image now runs ArozOS directly.

The base image digest and release URLs/checksums are pinned. Apt packages still resolve from live Debian repositories; this is not a bit-for-bit reproducible build. To update the application, review upstream release assets, update the pinned URLs and hashes, build and repeat these checks. Back up existing volumes and plan web-asset migration separately; the entrypoint intentionally preserves populated web volumes.
