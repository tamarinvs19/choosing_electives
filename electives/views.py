import json
from collections import defaultdict
from typing import cast

from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, FileResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET

from loguru import logger

from users.models import Person
from . import controller
from .models import Elective, StudentOnElective, ElectiveKind


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
    students = defaultdict(set)
    for sone in StudentOnElective.objects.filter(elective=elective).select_related('student').only('student'):
        students[sone.student].add(sone.kind.short_name)
    statistic = {
        kind: controller.get_statistics(elective, kind)
        for kind in elective.kinds.all()
    }
    context = {
        'elective': elective,
        'students': list(students.items()),
        'students_count': len(students),
        'kinds': [
            (data, statistic[data.kind])
            for data in controller.get_student_elective_kinds(user, elective)
        ]
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
        application = controller.change_kinds(user, elective_id, kind_id)
        elective = Elective.objects.get(id=elective_id)
        kind = ElectiveKind.objects.get(id=kind_id)
        students_count = controller.get_statistics(elective, kind)
        other_language_kind = None
        other_kind_counts = None
        other_short_name = None
        statistic = {
            kind: controller.get_statistics(elective, kind)
            for kind in elective.kinds.all()
        }
        current_short_names = list(set(
            data.kind.short_name
            for data in controller.get_student_elective_kinds(user, elective)
            if sum(statistic[data.kind].values()) > 0
        ))
        logger.debug(current_short_names)
        if application is not None:
            other_kind = application.elective.kinds.filter(
                semester=application.kind.semester,
                credit_units=application.kind.credit_units,
            ).exclude(
                language=application.kind.language,
            ).all()
            if len(other_kind) == 1:
                other_kind_counts = controller.get_statistics(elective, other_kind[0])
                other_language_kind = other_kind[0].id
                other_short_name = other_kind[0].short_name
        return JsonResponse({
            'move': application is not None,
            'students_count': students_count,
            'other_language_kind': other_language_kind,
            'other_kind_counts': other_kind_counts,
            'other_short_name': other_short_name,
            'current_short_names': current_short_names,
            'user_id': user.id,
            'student_name': str(user),
        })
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
        all_applications = StudentOnElective.objects.filter(
            student=student_on_elective.student,
            elective=student_on_elective.elective,
            kind=student_on_elective.kind
        )
        if student_on_elective is not None:
            return JsonResponse({
                'all_applications': [application.id for application in all_applications],
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
    new_index = request.POST.get('new_index', None)
    if student_on_elective_id is not None and target is not None and new_index is not None:
        sone = controller.attach_application(int(student_on_elective_id), target, new_index)
        if sone is None:
            response = {
                'OK': False,
            }
        else:
            response = {
                'OK': True,
                'semester': sone.kind.semester,
            }
        return JsonResponse(response)
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


@login_required
@require_GET
def get_application_rows(request, **kwargs):
    student = cast(Person, request.user)
    return JsonResponse({
        'codes_fall': controller.generate_application_row(student, 1),
        'codes_spring': controller.generate_application_row(student, 2),
        'credit_units_fall': {
            'sum': controller.calc_sum_credit_units(student, 1),
        },
        'credit_units_spring': {
            'sum': controller.calc_sum_credit_units(student, 2),
        },
        'credit_units_maybe_fall': {
            'sum': controller.calc_sum_credit_units(student, 1, False),
        },
        'credit_units_maybe_spring': {
            'sum': controller.calc_sum_credit_units(student, 2, False),
        },
    })


@login_required
@require_POST
def duplicate_application(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    if student_on_elective_id is not None:
        new_application = controller.duplicate_application(int(student_on_elective_id))
        prev_id = '#application-{0}-{1}{2}'.format(
            student_on_elective_id,
            1 if new_application.elective.has_fall else '',
            2 if new_application.elective.has_spring else ''
        )
        render_application = render_to_string(
            'account/application_card.html',
            context={'application': new_application},
            request=request,
        )
        return JsonResponse({
            'OK': True,
            'application': str(render_application),
            'prev_id': prev_id,
        })
    return HttpResponseBadRequest


@login_required
@require_GET
def download_table(request, **kwargs):
    workbook_name = controller.generate_summary_table()
    return FileResponse(open(workbook_name, 'rb'))
