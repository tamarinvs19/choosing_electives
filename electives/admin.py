from django.contrib import admin
from .models import Elective, StudentOnElective, KindOfElective, ElectiveKind, ElectiveThematic, \
    MandatoryThematicInStudentGroup, ApplicationCounter


class StudentOnElectiveInline(admin.TabularInline):
    model = StudentOnElective
    extra = 2


class KindOfElectiveInline(admin.TabularInline):
    model = KindOfElective
    extra = 1


class MandatoryThematicInline(admin.TabularInline):
    model = MandatoryThematicInStudentGroup
    extra = 1


class ElectiveAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'english_name', 'codename', 'description',
                           'english_description', 'thematic', 'text_teachers']}),
        ('Number of students', {'fields': ['min_number_students', 'max_number_students']}),
    ]
    inlines = [
        KindOfElectiveInline,
        StudentOnElectiveInline,
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
    inlines = [
        MandatoryThematicInline,
    ]
    list_display = ('name', 'english_name')


class ApplicationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['student', 'elective', 'kind', 'with_examination', 'attached', 'priority']}),
    ]
    list_display = ('student', 'elective', 'kind', 'attached', 'priority')


class ApplicationCounterAdmin(admin.ModelAdmin):
    list_display = (
        'thematic',
        'elective',
        'language',
        'semester',
        'credit_units',
        'attached',
        'count_of_applications',
    )


admin.site.register(Elective, ElectiveAdmin)
admin.site.register(ElectiveKind, ElectiveKindAdmin)
admin.site.register(ElectiveThematic, ElectiveThematicAdmin)
admin.site.register(StudentOnElective, ApplicationAdmin)
admin.site.register(ApplicationCounter, ApplicationCounterAdmin)
