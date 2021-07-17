from django.contrib import admin
from .models import Administrations, Teachers, Students, YearOfEducation, Curriculum


admin.site.register(Administrations)
admin.site.register(Teachers)
admin.site.register(Students)
admin.site.register(YearOfEducation)
admin.site.register(Curriculum)

