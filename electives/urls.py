from django.urls import path

from . import views

app_name = 'electives'
urlpatterns = [
    path('', views.open_elective_list, name='elective_list'),
    path('<int:elective_id>/', views.open_elective_page, name='elective_page'),
    path('<int:elective_id>/save_kinds', views.save_elective_kinds, name='save_kinds'),
    path('change_kind/', views.change_elective_kind, name='change_kind'),
    path('change_application_exam/', views.change_application_exam, name='change_application_exam'),
    path('change_application_kind/', views.change_application_kind, name='change_application_kind'),
    path('attach_application/', views.attach_application, name='attach_application'),
]

