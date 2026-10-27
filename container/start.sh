#!/bin/bash
set -euo pipefail
cd /arozos

# Keep each value as a single argument, including spaces and shell metacharacters.
args=()
options=(
    allow_autologin
    allow_cluster
    allow_iot
    allow_mdns
    allow_pkg_install
    allow_ssdp
    allow_upnp
    beta_scan
    bufffile_size
    buffpool_size
    cert
    console
    dir_list
    disable_http
    disable_ip_resolver
    disable_subservice
    enable_buffpool
    enable_hwman
    enable_pwman
    force_mac
    gzip
    homepage
    host
    hostname
    iobuf
    key
    logging
    max_upload_size
    ntt
    port
    public_reg
    root
    session_key
    skip_mdadm_reload
    storage_config
    tls
    tls_port
    tmp
    tmp_time
    upload_async
    upload_buf
    uuid
    version
    wlan_interface_name
    wpa_supplicant_config
)
for option in "${options[@]}"; do
    env_name="AROZOS_${option^^}"
    # An explicitly set prefixed variable takes precedence, even when empty.
    if [[ -v "$env_name" ]]; then
        args+=("-$option=${!env_name}")
    elif [[ -n "${!option:-}" ]]; then
        args+=("-$option=${!option}")
    fi
done

mkdir -p web files system
if [[ -z "$(ls -A web)" ]]; then
    echo 'Initializing ArozOS web assets...'
    tar -xzf web.tar.gz -C /arozos/
fi

# Do not log arguments: session_key can contain sensitive data.
exec ./arozos "${args[@]}" "$@"
