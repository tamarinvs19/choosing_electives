"""choosing_electives URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account import views as allauth_views
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('electives/', include('apps.electives.urls')),
    path('electives/admin/', admin.site.urls),
    path('electives/users/', include('apps.users.urls')),
    path(
        'electives/accounts/password/change/',
        login_required(
            allauth_views.PasswordChangeView.as_view(
                success_url='/electives/users/'
            )
        ),
        name='account_change_password'
    ),
    path('electives/accounts/', include('allauth.urls')),
    path('electives/parsing/', include('apps.parsing.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
