from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('<int:user_id>/', views.open_personal_page, name='personal_page'),
    path('<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
    path('change_group/', views.change_group, name='change_group'),
]

