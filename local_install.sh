
## PERSONNALISER CES VARIABLES

admin="admin"
passwd="adminadmin"
email="bla@bla.fr"

## FIN DE LA PERSONALISATION


app="compteur_du_gase"
project="compteur"
app_path=$(dirname $(realpath -s $0))
echo $app_path
final_path=$app_path/..
secret=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

echo "* Adding the user"
sudo useradd $app -d $final_path

echo "* Installing venv"
python3 -m venv $final_path/venv

venv_python=$final_path/venv/bin/python3
venv_pip=$final_path/venv/bin/pip

echo "* Installing python dependencies"
$venv_pip install pip --upgrade
$venv_pip install gunicorn
$venv_pip install -r $app_path/requirements.txt

echo "* Creating setting_local.py"
cat > $app_path/$project/settings_local.py << EOF
DEBUG = False
SECRET_KEY = '$secret'
ALLOWED_HOSTS = ['localhost']
STATIC_ROOT = '$final_path/static'
EOF

echo "* Creating log folder"
sudo mkdir -p /var/log/$app
sudo chown -R $app /var/log/$app
sudo chgrp -R www-data /var/log/$app

echo "* Changing permissions"
sudo chown -R $app:www-data $final_path

echo "* Migrations + Static"
sudo -u $app $venv_python $app_path/manage.py migrate --noinput
sudo -u $app $venv_python $app_path/manage.py collectstatic --noinput

echo "* Creating admin user"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${admin}', '${email}', '${passwd}')" | $venv_python $app_path/manage.py shell

echo "* Creating $final_path/gunicorn_config.py"
cat > $final_path/gunicorn_config.py << EOF
command = '$final_path/venv/bin/gunicorn'
pythonpath = '$app_path'
workers = 4
user = '$app'
bind = 'unix:$final_path/sock'
pid = '/run/gunicorn/$app-pid'
errorlog = '/var/log/$app/error.log'
accesslog = '/var/log/$app/access.log'
access_log_format = '%({X-Real-IP}i)s %({X-Forwarded-For}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = 'warning'
capture_output = True
EOF

echo "* Creating /etc/systemd/system/$app.service"
cat > /etc/systemd/system/$app.service << EOF
[Unit]
Description=Démon gunicorn pour le compteur du GASE
After=network.target

[Service]
PIDFile=/run/gunicorn/$app-pid
User=$app
Group=www-data
WorkingDirectory=$app_path
ExecStart=$final_path/venv/bin/gunicorn -c $final_path/gunicorn_config.py $project.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "* Creating /etc/nginx/sites-enabled/$app.conf"
cat > /etc/nginx/sites-enabled/$app.conf << EOF
server {
    listen 80;
    server_name localhost;

    location /static/ {
        root $final_path;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$final_path/sock;
    }
}
EOF

echo "* Removing /etc/nginx/sites-enabled/default"
sudo rm /etc/nginx/sites-enabled/default

echo "* Restarting Nginx"
sudo systemctl restart nginx

echo "* Enabling the service"
sudo systemctl daemon-reload
sudo systemctl start $app
sudo systemctl enable $app
