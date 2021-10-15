from django.contrib import admin
from .models import Elective, StudentOnElective, TeacherOnElective, KindOfElective, ElectiveKind, ElectiveThematic, \
    MandatoryElectiveForStudentGroup


class StudentOnElectiveInline(admin.TabularInline):
    model = StudentOnElective
    extra = 2


class TeacherOnElectiveInline(admin.TabularInline):
    model = TeacherOnElective
    extra = 1


class KindOfElectiveInline(admin.TabularInline):
    model = KindOfElective
    extra = 1


class MandatoryElectiveForStudentGroupInline(admin.TabularInline):
    model = MandatoryElectiveForStudentGroup
    extra = 1


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'codename', 'description', 'thematic']}),
        ('Number of students', {'fields': ['min_number_students', 'max_number_students']}),
    ]
    inlines = [KindOfElectiveInline, TeacherOnElectiveInline,
               StudentOnElectiveInline, MandatoryElectiveForStudentGroupInline]
    list_display = ('name',)
    search_fields = ['name']


class ElectiveKindAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['credit_units', 'language', 'semester']}),
    ]
    list_display = ('show_name',)


class ElectiveThematicAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    list_display = ('name',)


admin.site.register(Elective, ElectiveAdmin)
admin.site.register(ElectiveKind, ElectiveKindAdmin)
admin.site.register(ElectiveThematic, ElectiveThematicAdmin)

