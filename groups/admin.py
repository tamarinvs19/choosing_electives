from django.contrib import admin
from .models import StudentGroup, YearOfEducation, Curriculum, Student


class StudentGroupAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['curriculum', 'course_value']}),
        ('Fall', {'fields': [
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


class StudentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['person', 'student_group']})
    ]
    list_display = ('person', 'student_group')


admin.site.register(Student, StudentAdmin)
admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(YearOfEducation)
admin.site.register(Curriculum)
