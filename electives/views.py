import json
from collections import defaultdict
from typing import cast

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from loguru import logger

from users.models import Person
from . import controller
from .elective_statistic import Statistic
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
    students = defaultdict(list)
    for sone in StudentOnElective.objects.filter(elective=elective).select_related('student').only('student'):
        students[sone.student].append(sone.kind.short_name)
    logger.debug(students)
    context = {
        'elective': elective,
        'students': students.items(),
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
def change_application_exam(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    if student_on_elective_id is not None:
        student_on_elective_id = int(student_on_elective_id)
        student_on_elective = controller.change_exam(student_on_elective_id)
        if student_on_elective is not None:
            return JsonResponse({
                'with_exam': student_on_elective.with_examination,
                'credit_units': student_on_elective.credit_units,
                'OK': True,
            })
        else:
            return JsonResponse({
                'message': 'There are not any applications with received id.',
                'OK': False,
            })
    return HttpResponseBadRequest


@login_required
@require_POST
def change_application_kind(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    kind_id = request.POST.get('kind_id', None)
    if student_on_elective_id is not None and kind_id is not None:
        student_on_elective_id, kind_id = int(student_on_elective_id), int(kind_id)
        student_on_elective = controller.change_kind(student_on_elective_id, kind_id)
        if student_on_elective is not None:
            return JsonResponse({
                'full_kind': student_on_elective.kind.middle_name,
                'credit_units': student_on_elective.credit_units,
                'with_exam': student_on_elective.with_examination,
                'is_seminar': student_on_elective.is_seminar,
                'semester': student_on_elective.kind.semester,
                'OK': True,
            })
        else:
            return JsonResponse({
                'message': 'There are not any applications or kind with received ids.',
                'OK': False,
            })
    return HttpResponseBadRequest


@login_required
@require_POST
def attach_application(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    target = request.POST.get('target', None)
    if student_on_elective_id is not None and target is not None:
        sone = controller.attach_application(int(student_on_elective_id), target)
        if sone is None:
            response = {
                'OK': False,
            }
        else:
            response = {
                'OK': True,
                'semester': sone.kind.semester,
            }
        return JsonResponse({
        })
    return HttpResponseBadRequest


@login_required
@require_POST
def remove_application(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    if student_on_elective_id is not None:
        controller.remove_application(int(student_on_elective_id))
        return JsonResponse({
            'OK': True,
        })
    return HttpResponseBadRequest
