from django.urls import path

from . import views

app_name = 'parsing'
urlpatterns = [
    path('okhotin_table/', views.parsing_page, name='parsing'),
    path('google_table/', views.table_parsing_page, name='table_parsing'),
]

