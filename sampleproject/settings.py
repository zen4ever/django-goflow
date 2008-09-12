# Django settings for sampleproject project.
from os.path import dirname, join 
_dir = dirname(__file__)

LIB_PATH = join(_dir,'..')
import sys
sys.path.append(LIB_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = join(_dir,'data.sqlite')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(_dir, 'static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ih3^*u=ndnu+nbuv&0)zbd5m2gt%5alzu9*%s!bze2w&r426(6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'sampleproject.flags.loaders.filesystem.load_template_source',
    'sampleproject.flags.loaders.app_directories.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'sampleproject.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(_dir,'..', 'goflow', 'apptools', 'templates'),
    join(_dir,'..', 'goflow', 'runtime', 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'goflow.workflow',
    'goflow.runtime',
    'goflow.apptools',
    'sampleproject.sampleapp',
    'sampleproject.flags',
)

LOGIN_URL = '/accounts/login'

# user profile model
AUTH_PROFILE_MODULE = 'workflow.userprofile'

# mail notification
DEFAULT_FROM_EMAIL = 'sample@project.com'
EMAIL_HOST = 'localhost'

# user that executes auto processes
WF_USER_AUTO = 'auto'
# used to build application url like: http://[web_host]/[WF_APPS_PREFIX]/[application]
WF_APPS_PREFIX = '/sampleapp'
# used to find push functions
WF_PUSH_APPS_PREFIX = 'sampleproject.sampleapp.pushapps'

# test users for fast switch (with DEBUG=TRUE only)
TEST_USERS = (('admin','admin'), ('user1','user1'),
              ('user2','user2'), ('userg1','userg1'))

# the FLAGS_I18N_PREFIX parameter must match urls.py item:
# urls.py     > (r'^PREFIX/i18n/', include('django.conf.urls.i18n')),
# settings.py > FLAGS_I18N_PREFIX = '/PREFIX/i18n/'
FLAGS_I18N_PREFIX = '/lang/i18n/'
# flags served by local server
FLAGS_URL = MEDIA_URL + "flags/"
# flags served by net server
#FLAGS_URL = 'http://djangodev.free.fr/flags/'

# languages
ugettext = lambda s: s
LANGUAGES = (
    ('ar', ugettext('Arabic')),
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
    ('es', ugettext('Spanish')),
    ('de', ugettext('German')),
    ('pl', ugettext('Polish')),
)


