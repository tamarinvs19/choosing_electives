from django.contrib import admin
from .models import Elective, StudentOnElective, TeacherOnElective


class StudentOnElectiveInline(admin.TabularInline):
    model = StudentOnElective
    extra = 2


class TeacherOnElectiveInline(admin.TabularInline):
    model = TeacherOnElective
    extra = 1


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'credit_unit', 'description']}),
        ('Number of students', {'fields': ['min_number_students', 'max_number_students']}),
    ]
    inlines = [StudentOnElectiveInline, TeacherOnElectiveInline]
    list_display = ('name', 'credit_unit')
    list_filter = ['credit_unit']
    search_fields = ['name']


admin.site.register(Elective, ElectiveAdmin)

