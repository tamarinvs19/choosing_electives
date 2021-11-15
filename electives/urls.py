from django.urls import path

from . import views

app_name = 'electives'
urlpatterns = [
    path('', views.open_elective_list, name='elective_list'),
    path('<int:elective_id>/', views.open_elective_page, name='elective_page'),
    path('<int:elective_id>/save_kinds', views.save_elective_kinds, name='save_kinds'),
    path('change_kind/', views.change_elective_kind, name='change_kind'),
    path('change_exam/', views.change_exam, name='change_exam'),
]

