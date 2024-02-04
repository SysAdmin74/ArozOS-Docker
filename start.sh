#!/bin/bash
variable_list=("port" "hostname" "enable_hwman" "enable_pwman" "allow_autologin" "allow_cluster" "allow_iot" "allow_mdns" "allow_pkg_install" "allow_ssdp" "bufffile_size" "buffpool_size" "iobuf" "max_upload_size" "uuid")
command="./launcher"
for var_name in "${variable_list[@]}"; do
    if [ -n "${!var_name}" ]; then
        command+=" -${var_name}=${!var_name}"
    fi
done
echo "Running command: $command"
exec $command
