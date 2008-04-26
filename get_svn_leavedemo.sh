#!/bin/sh
echo 'export from svn'
svn export --force http://opensvn.csie.org/goflow/trunk .

chmod +x get_svn_leavedemo.sh
cd leave
chmod +x django.fcgi

cd ../leavedemo
PYTHONPATH=.. python manage.py syncdb
