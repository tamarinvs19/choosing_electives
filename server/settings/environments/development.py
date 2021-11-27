"""
This file contains all the settings that defines the development server.

SECURITY WARNING: don't run with debug turned on in production!
"""

from typing import List

from server.settings.components import config
from server.settings.components.common import INSTALLED_APPS, MIDDLEWARE

# Setting the development status:

DEBUG = True

ALLOWED_HOSTS = [
    config('DOMAIN_NAME'),
    '127.0.0.1',
]

# Is required for django-debug-toolbar to work
INTERNAL_IPS = [
    '127.0.0.1',
]


# Static files:
# https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-STATICFILES_DIRS

STATICFILES_DIRS: List[str] = []
