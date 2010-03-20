# Django settings for rain project.
from private_settings import *
import os

CURRENT_PATH = os.path.dirname(__file__)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#Databases moved to private settings

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/amedia/'

CURRENT_DOMAIN = '192.168.1.73:8080' #zeeb.us.to
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'media/')
MEDIA_URL = 'http://%s/media/' % CURRENT_DOMAIN

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'rain.userip.middleware.UpdateUserIPMiddleware',
)

ROOT_URLCONF = 'rain.urls'

TEMPLATE_DIRS = (
    os.path.join(CURRENT_PATH, 'templates/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'rain.invite_registration.context.add_new_invites',
    'rain.context.add_domain',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'rain.torrents',
    'rain.tracker',
    'rain.invite_registration',
    'rain.user_profiles',
    'rain.userip',
    'rain.ratio',
)

MAGIC_VALUES = {
  'time_until_inactive' : 30*60, #30 minutes
  'seed_interval' : 300, #5 minutes
  'peer_interval' : 30, #...
  'numwant_default' : 30, #30 should be plent as stated by spec
  'compact_default' : 0,  #1 for bandwidth, 0 for compatability
  
  #Don't change these. I mean you can but its pointless
  'seed' : 'S', 
  'peer' : 'P',
}

LOGIN_REDIRECT_URL = '/rain/torrents/'
