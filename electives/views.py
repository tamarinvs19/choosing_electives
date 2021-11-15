import json
from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from loguru import logger

from users.models import Person
from . import controller
from .models import Elective, ElectiveThematic, StudentOnElective, ElectiveKind


@login_required
def open_elective_list(request, **kwargs):
    user = cast(Person, request.user)
    groups = controller.get_electives_by_thematics(user)
    context = {
        'elective_groups': groups,
    }
    return render(request, 'electives/elective_list.html', context)


@login_required
def open_elective_page(request, elective_id, **kwargs):
    user = cast(Person, request.user)
    elective = Elective.objects.get(id=elective_id)
    students = {
        soe.student for soe in
        StudentOnElective.objects.filter(elective=elective).select_related('student').only('student')
    }
    context = {
        'elective': elective,
        'students': students,
        'students_count': len(students),
        'kinds': controller.get_student_elective_kinds(user, elective),
    }
    return render(request, 'electives/elective_page.html', context)


@login_required
@require_POST
def save_elective_kinds(request, elective_id, **kwargs):
    elective = Elective.objects.get(id=elective_id)
    user = cast(Person, request.user)
    kinds = request.POST.getlist('kinds', [])
    controller.save_kinds(user, elective, kinds)

    return HttpResponse(json.dumps({'OK': True}))


@login_required
@require_POST
def change_elective_kind(request, **kwargs):
    user = cast(Person, request.user)
    kind_id = request.POST.get('kind_id', None)
    elective_id = request.POST.get('elective_id', None)
    if kind_id is not None and elective_id is not None:
        elective_id, kind_id = int(elective_id), int(kind_id)
        controller.change_kinds(user, elective_id, kind_id)
        elective = Elective.objects.get(id=elective_id)
        kind = ElectiveKind.objects.get(id=kind_id)
        students_counts = {kind.id: count for kind, count in controller.get_statistics(elective).items()}
        if kind.id in students_counts:
            students_count = students_counts[kind.id]
        else:
            students_count = 0
        return JsonResponse({'students_count': students_count})
    return HttpResponseBadRequest


@login_required
@require_POST
def change_exam(request, **kwargs):
    user = cast(Person, request.user)
    kind_id = request.POST.get('kind_id', None)
    elective_id = request.POST.get('elective_id', None)
    if kind_id is not None and elective_id is not None:
        elective_id, kind_id = int(elective_id), int(kind_id)
        with_exam = controller.change_exam(user, elective_id, kind_id)
        if with_exam is not None:
            return JsonResponse({
                'with_exam': with_exam,
                'credit_units':
                    StudentOnElective.objects.get(
                        student=user, elective_id=elective_id, kind_id=kind_id
                    ).credit_units,
                'OK': True,
            })
        else:
            return JsonResponse({
                'message': 'There are not any applications with received elective and kind',
                'OK': False,
            })
    return HttpResponseBadRequest
