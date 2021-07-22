from django.contrib import admin
from .models import StudentGroup, YearOfEducation, Curriculum


class StudentGroupAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['curriculum', 'course_value']}),
        ('Authumn', {'fields': ['min_credit_unit_autumn', 'max_credit_unit_autumn', 'min_number_of_exams_autumn']}),
        ('Spring', {'fields': ['min_credit_unit_spring', 'max_credit_unit_spring', 'min_number_of_exams_spring']}),
    ]
    list_display = ('curriculum', 'course_value')

admin.site.register(StudentGroup, StudentGroupAdmin)
admin.site.register(YearOfEducation)
admin.site.register(Curriculum)

