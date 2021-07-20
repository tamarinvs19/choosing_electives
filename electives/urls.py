from django.urls import path

from . import views

app_name = 'electives'
urlpatterns = [
    path('', views.open_elective_list, name='elective_list'),
]

