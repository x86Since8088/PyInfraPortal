#!/bin/bash

# get OS type
os=$(uname -s| tr '[:upper:]' '[:lower:]')

bash --rcfile <(echo '. ~/.bashrc; cd /home/username/git/PySite/django/myproject; source /home/username/git/PySite/venv/bin/activate; python manage.py runserver
