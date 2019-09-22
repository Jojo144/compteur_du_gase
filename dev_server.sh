#!/bin/sh

# first time, uncoment
#~ python3 manage.py createsuperuser << EOF
#~
#~ titi@toto.fr
#~ admin
#~ admin
#~ y
#~ EOF

python3 manage.py makemigrations 
python3 manage.py migrate
python3 manage.py runserver
