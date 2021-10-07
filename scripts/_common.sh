#!/bin/bash

pkg_dependencies="python3-pip python3-virtualenv python3-venv python3-wheel sqlite3"

set_initial_permissions() {
    ynh_permission_url --permission="main" --url="/"

    ynh_permission_create \
        --label "Page d'accueil (horaires/permanences…)" \
        --permission="home_page" \
        --url="/$" \
        --additional_urls="/activité" "/static" \
        --allowed="all_users"

    ynh_permission_create \
        --permission="ynh_auth" \
        --url="/ynh_auth" \
        --allowed="all_users" \
        --protected=true
        --show_tile="false"
}
