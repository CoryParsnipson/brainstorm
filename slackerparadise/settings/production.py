"""
Django settings for slackerparadise project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

import dj_database_url  # heroku postgres adapter

import paths
import common


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# instatiate keyring object
keyring = common.KeyRing()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
keyring.set("SECRET_KEY", SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    '.slackerparadise.com',
    '.slackerparadise.herokuapp.com'
]

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party applications
    'imagekit',
    'storages',  # for media/static files serving from AWS S3

    # user applications
    'blog',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'slackerparadise.urls'

WSGI_APPLICATION = 'slackerparadise.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(),
}

# enable connection pooling
DATABASES['default']['ENGINE'] = 'django_postgrespool'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Flash Message settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# AWS S3 storage for media and static files
AWS_QUERYSTRING_AUTH = False
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
AWS_ASSOCIATE_TAG = os.environ['AWS_ASSOCIATE_TAG']

keyring.set("AWS_ACCESS_KEY_ID", AWS_ACCESS_KEY_ID)
keyring.set("AWS_SECRET_ACCESS_KEY", AWS_SECRET_ACCESS_KEY)
keyring.set("AWS_STORAGE_BUCKET_NAME", AWS_STORAGE_BUCKET_NAME)
keyring.set("AWS_ASSOCIATE_TAG", AWS_ASSOCIATE_TAG)

# media files
MEDIA_URL = 'http://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = paths.MEDIA_DIR

# rebuild media paths
paths.MEDIA_ROOT = MEDIA_URL
paths.MEDIA_IMAGE_ROOT = os.path.join(paths.MEDIA_ROOT, paths.MEDIA_IMAGE_DIR)
paths.MEDIA_VIDEO_ROOT = os.path.join(paths.MEDIA_ROOT, paths.MEDIA_VIDEO_DIR)
paths.MEDIA_FILE_ROOT = os.path.join(paths.MEDIA_ROOT, paths.MEDIA_FILE_DIR)

DEFAULT_FILE_STORAGE = "slackerparadise.s3utils.MediaS3BotoStorage"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = 'http://%s.s3.amazonaws.com/static/' % AWS_STORAGE_BUCKET_NAME
STATIC_ROOT = '/' + paths.STATIC_ROOT + '/'
paths.STATIC_DIR = STATIC_URL

STATICFILES_STORAGE = "slackerparadise.s3utils.StaticS3BotoStorage"

# Template dirs
# keep global, non-app specific template files here
TEMPLATE_DIRS = (paths.TEMPLATE_DIR, )

# have request template variable automatically
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)