"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings
https://sobolevn.me/2017/04/managing-djangos-settings

To change settings file:
`DJANGO_ENV=production python manage.py runserver`
"""

from os import environ

from split_settings.tools import include, optional

# Managing environment via DJANGO_ENV variable:
environ.setdefault('DJANGO_ENV', 'development')
_ENV = environ['DJANGO_ENV']

_base_settings = (
    'components/common.py',

    # Select the right env:
    'environments/{0}.py'.format(_ENV),
)

# Include settings:
include(*_base_settings)
