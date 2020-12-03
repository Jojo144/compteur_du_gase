#!/bin/bash

pkg_dependencies="python3-pip python3-virtualenv python3-venv python3-wheel sqlite3"

handle_is_home_public() {
    if [[ $is_home_public -eq 1 ]]; then
        domainregex=$(echo "$domain" | sed 's/-/\%&/g')
        if [ "$path" = "/" ]
        then
            # to avoid "//static"
            pathregex=""
        else
            pathregex=$(echo "$path" | sed 's/-/\%&/g')
        fi
        ynh_app_setting_set "$app" skipped_regex "$domainregex$pathregex/$","$domainregex$pathregex/activité","$domainregex$pathregex/static"
    else
        # Do not skip anything : protect everything
        ynh_app_setting_delete "$app" skipped_regex
    fi
}
