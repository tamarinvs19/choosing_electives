
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from electives import controller
from electives.models import Elective, StudentOnElective


@login_required
def open_personal_page(request, **kwargs):
    context = {}
    return render(request, 'account/personal_page.html', context)


@login_required
def open_sorting_page(request, user_id, **kwargs):
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
    }
    return render(request, 'account/sort_electives.html', context)

