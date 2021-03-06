from django.urls import path

from . import views

app_name = 'electives'
urlpatterns = [
    path('', views.open_elective_list, name='elective_list'),
    path('<int:elective_id>/', views.open_elective_page, name='elective_page'),
    path('change_kind/', views.change_elective_kind, name='change_kind'),
    path('change_application_exam/', views.change_application_exam, name='change_application_exam'),
    path('change_application_kind/', views.change_application_kind, name='change_application_kind'),
    path('apply_application/', views.apply_application, name='apply_application'),
    path('remove_application/', views.remove_application, name='remove_application'),
    path('duplicate_application/', views.duplicate_application, name='duplicate_application'),
    path('get_application_rows/', views.get_application_rows, name='get_application_rows'),
    path('download_table/', views.download_table, name='download_table'),
    path('download_applications_table/', views.download_applications_table, name='download_applications_table'),
    path('applications/<int:user_id>/', views.open_sorting_page, name='sorting_page'),
    path('restart_counter/', views.restart_counter, name='restart_counter'),
    path('save_opened_thematic/', views.save_opened_thematic, name='save_opened_thematic'),
    path('save_cookie/', views.save_cookie, name='save_cookie'),
]

