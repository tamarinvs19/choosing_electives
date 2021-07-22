from django.urls import path

from . import views

app_name = 'electives'
urlpatterns = [
    path('', views.open_elective_list, name='elective_list'),
    path('<int:elective_id>/', views.open_elective_page, name='elective_page'),
]

