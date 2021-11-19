from django.contrib import admin
from .models import StudentGroup, YearOfEducation, Curriculum


class StudentGroupAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['curriculum', 'course_value']}),
        ('Autumn', {'fields': [
            'min_credit_unit_autumn',
            'max_credit_unit_autumn',
            'min_number_of_exams_autumn',
            'max_number_of_exams_autumn',
            'max_light_credit_unit_autumn',
            'max_cs_courses_autumn',
        ]}),
        ('Spring', {'fields': [
            'min_credit_unit_spring',
            'max_credit_unit_spring',
            'min_number_of_exams_spring',
            'max_number_of_exams_spring',
            'max_light_credit_unit_spring',
            'max_cs_courses_spring',
        ]}),
    ]
    list_display = ('curriculum', 'course_value')


admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(YearOfEducation)
admin.site.register(Curriculum)
