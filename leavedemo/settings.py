# Django settings for openflow project.
from os.path import dirname, join 
_dir = dirname(__file__)

LIB_PATH = join(_dir,'..')
import sys
sys.path.append(LIB_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

LOGIN_URL = 'accounts/login/'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = join(_dir, 'sqlite.db3')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(_dir, 'media/files/')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/files/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%@48o#l@iz!ybjl_2_1smc#%*u+^m0m^18ghw-6=3k48g2rt8^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'leavedemo.urls'

TEMPLATE_DIRS = (
    join(_dir,'..', 'goflow', 'apptools', 'templates'),
    join(_dir,'..', 'goflow', 'runtime', 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'goflow.workflow',
    'goflow.graphics2',
    'goflow.runtime',
    'goflow.apptools',
    'leavedemo.leave',
)

# user profile model
AUTH_PROFILE_MODULE = 'workflow.userprofile'

TEST_USERS = (
            ('primus','p'),('notarius','n'),('prefectus','p'),
            ('socius','s'),('secundus','s'),('tertius','t'),('quartus','q')
)
WF_USER_AUTO = 'auto'
WF_APPS_PREFIX = '/leave'
WF_PUSH_APPS_PREFIX = 'leavedemo.leave.pushapplications'

# mail notification settings
DEFAULT_FROM_EMAIL = 'goflow <goflow@alwaysdata.net>'
EMAIL_HOST = 'smtp.alwaysdata.com'
EMAIL_SUBJECT_PREFIX = '[Goflow notification]'
