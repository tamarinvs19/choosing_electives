from django.contrib import admin
from .models import Elective


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'credit_unit']}),
    ]
    list_display = ('name', 'credit_unit')
    list_filter = ['credit_unit']
    search_fields = ['name']


admin.site.register(Elective, ElectiveAdmin)

