from django.contrib import admin
from .models import Elective, StudentOnElective, TeacherOnElective, KindOfElective, ElectiveKind


class StudentOnElectiveInline(admin.TabularInline):
    model = StudentOnElective
    extra = 2


class TeacherOnElectiveInline(admin.TabularInline):
    model = TeacherOnElective
    extra = 1


class KindOfElectiveInline(admin.TabularInline):
    model = KindOfElective
    extra = 1


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'codename', 'description']}),
        ('Number of students', {'fields': ['min_number_students', 'max_number_students']}),
    ]
    inlines = [KindOfElectiveInline, TeacherOnElectiveInline, StudentOnElectiveInline]
    list_display = ('name',)
    search_fields = ['name']


class ElectiveKindAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['credit_units', 'language', 'semester']}),
    ]
    list_display = ('show_name',)


admin.site.register(Elective, ElectiveAdmin)
admin.site.register(ElectiveKind, ElectiveKindAdmin)

