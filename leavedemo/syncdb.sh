#!/bin/sh
chmod +x django.fcgi
echo 'init db (syncdb); answer no when create admin asked.'
python manage.py --pythonpath=.. syncdb
