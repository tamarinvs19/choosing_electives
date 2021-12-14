
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from electives import controller
from electives.models import Elective, StudentOnElective
from groups.models import Student
from users.models import Person


@login_required
def open_personal_page(request, **kwargs):
    context = {}
    return render(request, 'electives/personal_page.html', context)


@login_required
def open_sorting_page(request, user_id, **kwargs):
    person = Person.objects.get(id=user_id)
    applications_fall = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=1,
        attached=False,
    ).order_by('priority').all()
    applications_spring = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=2,
        attached=False,
    ).order_by('priority').all()
    applications_fall_attached = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=1,
        attached=True,
    ).order_by('priority').all()
    applications_spring_attached = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=2,
        attached=True,
    ).order_by('priority').all()
    context = {
        'applications_fall': applications_fall,
        'applications_spring': applications_spring,
        'applications_fall_attached': applications_fall_attached,
        'applications_spring_attached': applications_spring_attached,
        'fall_code_row': controller.generate_application_row(student=user_id, semester=1),
        'spring_code_row': controller.generate_application_row(student=user_id, semester=2),
        'credit_units_fall': {
            'max': person.student_data.student_group.max_credit_unit_fall,
            'min': person.student_data.student_group.min_credit_unit_fall,
            'sum': controller.calc_sum_credit_units(person, 1),
        },
        'credit_units_maybe_fall': {
            'sum': controller.calc_sum_credit_units(person, 1, False),
        },
        'credit_units_maybe_spring': {
            'sum': controller.calc_sum_credit_units(person, 2, False),
        },
        'credit_units_spring': {
            'max': person.student_data.student_group.max_credit_unit_spring,
            'min': person.student_data.student_group.min_credit_unit_spring,
            'sum': controller.calc_sum_credit_units(person, 2),
        },
    }
    return render(request, 'electives/sort_electives.html', context)

