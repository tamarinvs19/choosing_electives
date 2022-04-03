from django.contrib import admin
from .models import Person, Invitation


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('deadline', 'link')


admin.site.register(Person)
admin.site.register(Invitation, InvitationAdmin)
