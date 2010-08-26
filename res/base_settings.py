# -*- coding: utf-8 -*-

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

try:
    username = os.environ["USERNAME"] if "USERNAME" in os.environ else os.environ["USER"]
    exec 'from settings_%s import *' % username
except ImportError:
    try:
        exec 'from settings_production import *'
    except ImportError:
        print "Couldn't import settings for user %s or production" % username

TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Moscow' # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
LANGUAGE_CODE = 'en-us' # http://www.i18nguy.com/unicode/language-identifiers.html
SITE_ID = 1
USE_I18N = True
USE_L10N = True

DOCUMENT_ROOT = '{{ document_root }}'
MEDIA_ROOT = DOCUMENT_ROOT+'media/'
MEDIA_URL = SITE_HTTP+'media/'
ADMIN_MEDIA_PREFIX = SITE_HTTP + 'media/admin/'

SECRET_KEY = '{{ secret_key }}'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = '{{ project_name }}.urls'

TEMPLATE_DIRS = (
    DOCUMENT_ROOT+'app/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
)
