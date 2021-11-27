"""
Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from server.apps.elective import urls as elective_urls

urlpatterns = [
    # Apps:
    path('electives/', include(elective_urls, namespace='elective')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
]
