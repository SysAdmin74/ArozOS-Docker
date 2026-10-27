# ArozOS-Docker

Docker packaging for [ArozOS by tobychui](https://github.com/tobychui/arozos), using the upstream prebuilt binaries and web assets. This repository maintains the container integration; the application is developed upstream.

## Quick start

Requires an x86-64 Docker host and Docker Compose 2.24 or newer.

```sh
cp .env.example .env
# Edit .env to configure ArozOS.
docker compose up -d --build
```

Open port 8980 on your Docker host. Data persists under `container/data/{files,web,system}`. Apply environment changes with `docker compose up -d` (a restart alone does not update container variables). Existing web assets are preserved; rebuilding does not upgrade an already populated web volume.

## Environment configuration

See the [environment configuration wiki](Wiki.md) for the complete variable reference, precedence rules, Docker and Compose examples, HTTPS configuration, persistent storage, and upgrade instructions.

All supported upstream flags map to `AROZOS_*` variables. Legacy lowercase names remain supported. The image runs ArozOS directly so Docker can stop it cleanly; upgrades use image rebuilds instead of the upstream launcher.

## Validation

```sh
python3 -m unittest discover -s tests -v
docker compose config --quiet
docker compose build
```

The argument tests exercise the entrypoint with a stub executable without starting ArozOS.
