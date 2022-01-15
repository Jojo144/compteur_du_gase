#!/bin/bash

pkg_dependencies="python3-pip python3-virtualenv python3-venv python3-wheel sqlite3 build-essential python3-dev python3-dev libldap2-dev libsasl2-dev ldap-utils"

set_initial_permissions() {
    ynh_permission_url --permission="main" --url="/"

    if ! ynh_permission_exists --permission="home_page"
    then
        ynh_permission_create \
            --label "Page d\'accueil" \
            --permission="home_page" \
            --url="/$" \
            --additional_urls="/activité" "/static" \
            --allowed="visitors"
    fi

    if ! ynh_permission_exists --permission="admin"
    then
       ynh_permission_create \
           --label "Panneau d\'administration" \
           --permission="admin" \
           --allowed="$admin" \
           --protected=true \
           --show_tile="false"
    fi
}
