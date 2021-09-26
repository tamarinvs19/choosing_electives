from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('<int:user_id>/', views.open_personal_page, name='personal_page'),
    path('<int:user_id>/electives/', views.open_sorting_page, name='sorting_page'),
]

