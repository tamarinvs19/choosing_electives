from typing import cast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest

from loguru import logger

from groups.models import StudentGroup, Student
from users.models import Person


@login_required
def open_personal_page(request, **kwargs):
    student = cast(Person, request.user)
    context = {
        'groups': sorted(StudentGroup.objects.all(), key=lambda group: str(group)),
    }
    if Student.objects.filter(person=student).exists():
        context['current_group'] = student.student_data.student_group
        context['has_group'] = True
    else:
        context['has_group'] = False
    return render(request, 'electives/personal_page.html', context)


@login_required
def change_group(request, **kwargs):
    student = cast(Person, request.user)
    group_id = request.POST.get('group_id', None)
    logger.debug(group_id)
    if group_id is not None:
        if Student.objects.filter(person=student).exists():
            student.student_data.student_group_id = group_id
            student.student_data.save()
        else:
            Student.objects.create(
                person=student,
                student_group=StudentGroup.objects.get(id=group_id),
            )
        return JsonResponse({'OK': True})
    return HttpResponseBadRequest
