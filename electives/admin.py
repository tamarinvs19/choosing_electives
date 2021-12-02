from django.contrib import admin
from .models import Elective, StudentOnElective, TeacherOnElective, KindOfElective, ElectiveKind, ElectiveThematic, \
    MandatoryElectiveInStudentGroup


class StudentOnElectiveInline(admin.TabularInline):
    model = StudentOnElective
    extra = 2


class KindOfElectiveInline(admin.TabularInline):
    model = KindOfElective
    extra = 1


class MandatoryElectiveForStudentGroupInline(admin.TabularInline):
    model = MandatoryElectiveInStudentGroup
    extra = 1


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'english_name', 'codename', 'description',
                           'english_description', 'thematic', 'text_teachers']}),
        ('Number of students', {'fields': ['min_number_students', 'max_number_students']}),
    ]
    inlines = [KindOfElectiveInline,
               StudentOnElectiveInline,
               MandatoryElectiveForStudentGroupInline,
               ]
    list_display = ('name',)
    search_fields = ['name']


class ElectiveKindAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['credit_units', 'language', 'semester']}),
    ]
    list_display = ('show_name',)


class ElectiveThematicAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'english_name']}),
    ]
    list_display = ('name', 'english_name')


admin.site.register(Elective, ElectiveAdmin)
admin.site.register(ElectiveKind, ElectiveKindAdmin)
admin.site.register(ElectiveThematic, ElectiveThematicAdmin)

