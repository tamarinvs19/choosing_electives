"""Django settings for choosing_electives project."""

import os
from pathlib import Path

from my_environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(
    DEBUG=(True, bool),
)
env.read_env(file_name='.env')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or env['DJANGO_SECRET_KEY']

DEBUG = env['DEBUG']

ALLOWED_HOSTS = [
    "*",
    'localhost',
    '127.0.0.1',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Application definition

INSTALLED_APPS = [
    'apps.electives',
    'apps.groups',
    'apps.users',
    'apps.parsing',

    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.slack',

    'constance',
]

SITE_ID = 1
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'slack': {
        'APP': {
            'client_id': os.environ.get('SLACK_CLIENT_ID') or env['SLACK_CLIENT_ID'],
            'secret': os.environ.get('SLACK_SECRET') or env['SLACK_SECRET'],
        },
        'SCOPE': ['identity.basic', 'openid', 'profile', 'email'],
    }
}

LOGIN_URL = '/electives/accounts/login/'
LOGIN_REDIRECT_URL = '/electives/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/electives/accounts/login/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/electives/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') or env['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') or env['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587
EMAIL_USE_TLS = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'choosing_electives.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'choosing_electives.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_NAME') or env['POSTGRES_NAME'],
        'USER': os.environ.get('POSTGRES_USER') or env['POSTGRES_USER'],
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD') or env['POSTGRES_PASSWORD'],
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=15000ms',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/electives/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'compressed_static')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
