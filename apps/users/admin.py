from django.contrib import admin
from .models import Person


# class PersonAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None, {'fields': ['username', 'password', 'first_name', 'last_name']}),
#     ]
#
#
admin.site.register(Person)
