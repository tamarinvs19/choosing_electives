from django.urls import path

from . import views

app_name = 'parsing'
urlpatterns = [
    path('', views.parsing_page, name='parsing'),
]

