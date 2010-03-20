import os, sys
 
#Calculate the path based on the location of the WSGI script.
apache_configuration = os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace)
sys.path.append(project)

os.environ['DJANGO_SETTINGS_MODULE'] = 'rain.settings'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
  #import logging
  #logging.error(environ)
  #environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
  return _application(environ, start_response)