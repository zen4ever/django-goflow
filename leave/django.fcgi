#!/usr/bin/python
import os, sys
sys.path.insert(0, "/home/goflow/www/")
os.environ['DJANGO_SETTINGS_MODULE'] = "leavedemo.settings"
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
