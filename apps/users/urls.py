from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('', views.redirect_to_personal_page, name='redirect_personal_page'),
    path('invite/', views.invite, name='invite'),
    path('<int:user_id>/', views.open_personal_page, name='personal_page'),
    path('<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
]

