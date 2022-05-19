from collections import defaultdict
from typing import cast

from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, FileResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET, last_modified

from loguru import logger

from apps.groups.models import Student
from apps.parsing.models import ConfigModel
from apps.users.models import Person
from apps.electives import logic
from apps.electives.elective_statistic import Statistic
from apps.electives.models import Elective, StudentOnElective, ElectiveKind, ElectiveThematic


def last_modified_func(request, **kwargs):
    return Statistic().last_modified


@login_required
@last_modified(last_modified_func)
def open_elective_list(request, **kwargs):
    user = cast(Person, request.user)
    groups = logic.get_electives_by_thematics(user)
    config, _ = ConfigModel.objects.get_or_create()
    groups_with_opened_thematics = [
        (thematic, electives, request.session.get(thematic['short_name'], False))
        for thematic, electives in groups
    ]

    context = {
        'elective_groups': groups_with_opened_thematics,
        'block_fall': config.block_fall,
        'block_fall_applications': config.block_fall_applications,
        'block_spring_applications': config.block_spring_applications,
        'show_menu': request.session.get('show_menu', True),
    }
    return render(request, 'electives/elective_list.html', context)


@login_required
@require_POST
def save_opened_thematic(request, **kwargs):
    switch_all = request.POST.get('all', None)
    if switch_all is not None:
        thematics = ElectiveThematic.objects.all().only('short_name')
        is_opened = request.POST.get('is_opened', False)
        for thematic in thematics:
            request.session[thematic.short_name] = is_opened
    else:
        thematic_name = request.POST.get('thematic_name', None)
        if thematic_name is not None:
            request.session[thematic_name] = not request.session.get(thematic_name, False)
    return JsonResponse({'OK': True})


@login_required
@require_POST
def save_cookie(request, **kwargs):
    cookie_field = request.POST.get('cookie_field', None)
    cookie_value = request.POST.get('cookie_value', None)
    if cookie_field is not None:
        request.session[cookie_field] = cookie_value
        response = {'OK': True}
    else:
        response = {'OK': False}
    return JsonResponse(response)


@login_required
@require_GET
def open_elective_page(request, elective_id, **kwargs):
    user = cast(Person, request.user)
    elective = Elective.objects.get(id=elective_id)
    students = defaultdict(set)
    for application in StudentOnElective.objects.filter(
        elective=elective,
    ).select_related('student').only('student'):
        students[application.student].add((application.kind.short_name, not application.potential))
    statistic = {
        kind: logic.get_statistics(elective, kind)
        for kind in elective.kinds.all()
    }
    config, _ = ConfigModel.objects.get_or_create()
    context = {
        'elective': elective,
        'students': list(students.items()),
        'students_count': len(students),
        'kinds': [
            (data, statistic[data.kind])
            for data in logic.get_student_elective_kinds(user, elective)
        ],
        'show_student_names': config.show_student_names,
    }
    return render(request, 'electives/elective_page.html', context)


@login_required
@require_POST
def change_elective_kind(request, **kwargs):
    user = cast(Person, request.user)
    kind_id = request.POST.get('kind_id', None)
    elective_id = request.POST.get('elective_id', None)

    if kind_id is not None and elective_id is not None:
        elective_id, kind_id = int(elective_id), int(kind_id)
        elective = Elective.objects.get(id=elective_id)
        kind = ElectiveKind.objects.get(id=kind_id)

        application = logic.change_kinds(user, elective, kind)
        students_count = logic.get_statistics(elective, kind)

        other_language_kind = None
        other_kind_counts = None
        other_short_name = None
        if application is not None:
            other_kind = application.elective.kinds.filter(
                semester=application.kind.semester,
                credit_units_kind__credit_units=application.kind.credit_units,
            ).exclude(
                language=application.kind.language,
            ).all()
            if len(other_kind) == 1:
                other_kind_counts = logic.get_statistics(elective, other_kind[0])
                other_language_kind = other_kind[0].id
                other_short_name = other_kind[0].short_name
        statistic = Statistic()

        current_short_names = [
            (application.kind.short_name, not application.potential)
            for application in StudentOnElective.objects.filter(
                elective=elective,
                student=user,
            ).only('kind', 'potential')
        ]
        only_names = [name for name, _ in current_short_names]
        current_unused_names = [
            kind.short_name
            for kind in elective.kinds.all()
            if kind.short_name not in only_names
        ]

        response = {
            'move': application is not None,
            'students_count': students_count,
            'other_language_kind': other_language_kind,
            'other_kind_counts': other_kind_counts,
            'other_short_name': other_short_name,
            'current_short_names': current_short_names,
            'current_unused_names': current_unused_names,
            'user_id': user.id,
            'thematic_id': elective.thematic.id,
            'fall_count': statistic.data[elective.thematic.pk][elective.pk].student_count(1),
            'spring_count': statistic.data[elective.thematic.pk][elective.pk].student_count(2),
        }
        config = ConfigModel()
        if config.show_student_names:
            response['student_name'] = Person.__str__(user)

        return JsonResponse(response)
    return HttpResponseBadRequest


@login_required
@require_POST
def change_application_exam(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    if student_on_elective_id is not None:
        student_on_elective_id = int(student_on_elective_id)
        student_on_elective = StudentOnElective.objects.get(
            pk=student_on_elective_id
        )
        student_on_elective = logic.change_exam(student_on_elective)
        if student_on_elective is not None:
            return JsonResponse({
                'with_exam': student_on_elective.with_examination,
                'credit_units': student_on_elective.credit_units,
                'OK': True,
            })
        else:
            return JsonResponse({
                'message': 'Can not change examination',
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
        student_on_elective = StudentOnElective.objects.get(
            pk=student_on_elective_id,
        )
        kind = ElectiveKind.objects.get(pk=kind_id)
        student_on_elective = logic.change_kind(student_on_elective, kind)
        if student_on_elective is not None:
            all_applications = StudentOnElective.objects.filter(
                student=student_on_elective.student,
                elective=student_on_elective.elective,
                kind=student_on_elective.kind
            )
            return JsonResponse({
                'all_applications': [application.id for application in all_applications],
                'full_kind': student_on_elective.kind.middle_name,
                'credit_units': student_on_elective.credit_units,
                'with_exam': student_on_elective.with_examination,
                'only_without_exam': student_on_elective.kind_of_elective.only_without_exam,
                'only_with_exam': student_on_elective.kind_of_elective.only_with_exam,
                'semester': student_on_elective.kind.semester,
                'OK': True,
            })
        else:
            return JsonResponse({
                'message': 'Can not change kind',
                'OK': False,
            })
    return HttpResponseBadRequest


@login_required
@require_POST
def apply_application(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    target = request.POST.get('target', None)
    new_index = request.POST.get('new_index', None)
    if student_on_elective_id is not None and target is not None and new_index is not None:
        student_on_elective = StudentOnElective.objects.get(pk=int(student_on_elective_id))
        sone = logic.apply_application(student_on_elective, target, int(new_index))
        if sone is None:
            response = {
                'OK': False,
                'message': 'Can not move application',
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
        application = StudentOnElective.objects.get(pk=int(student_on_elective_id))
        success = logic.remove_applications(application)
        if success:
            return JsonResponse({
                'OK': True,
            })
        else:
            return JsonResponse({
                'OK': False,
                'message': 'Can not remove application',
            })
    return HttpResponseBadRequest


@login_required
@require_GET
def get_application_rows(request, **kwargs):
    student = cast(Person, request.user)
    fall_sum = logic.calc_sum_credit_units(student, 1)
    fall_min = student.student_data.student_group.min_credit_unit_fall
    spring_sum = logic.calc_sum_credit_units(student, 2)
    spring_min = student.student_data.student_group.min_credit_unit_spring
    return JsonResponse({
        'codes_fall': logic.generate_application_row(student, 1),
        'codes_spring': logic.generate_application_row(student, 2),
        'credit_units_fall': {
            'sum': fall_sum,
            'min': fall_min,
            'is_too_few': int(fall_min > fall_sum),
        },
        'credit_units_spring': {
            'sum': spring_sum,
            'min': spring_min,
            'is_too_few': int(spring_min > spring_sum),
        },
        'credit_units_potential_fall': {
            'sum': logic.calc_sum_credit_units(student, 1, True),
        },
        'credit_units_potential_spring': {
            'sum': logic.calc_sum_credit_units(student, 2, True),
        },
    })


@login_required
@require_POST
def duplicate_application(request, **kwargs):
    student_on_elective_id = request.POST.get('student_on_elective_id', None)
    if student_on_elective_id is not None:
        application = StudentOnElective.objects.get(pk=int(student_on_elective_id))
        new_application = logic.duplicate_application(application)
        if new_application is not None:
            prev_id = '#application-{0}-{1}{2}'.format(
                student_on_elective_id,
                1 if new_application.elective.has_fall else '',
                2 if new_application.elective.has_spring else ''
            )
            render_application = render_to_string(
                'electives/application_card.html',
                context={'application': new_application},
                request=request,
            )
            return JsonResponse({
                'OK': True,
                'application': str(render_application),
                'prev_id': prev_id,
            })
        else:
            return JsonResponse({
                'OK': False,
                'message': 'Can not duplicate application'
            })
    return HttpResponseBadRequest


@login_required
@require_GET
def download_table(request, **kwargs):
    workbook_name = logic.generate_summary_table()
    return FileResponse(open(workbook_name, 'rb'))


@login_required
@require_GET
def open_sorting_page(request, user_id, **kwargs):
    person = Person.objects.get(id=user_id)

    if not Student.objects.filter(person=person).exists():
        return redirect('/electives/users/{0}/'.format(person.id))

    config, _ = ConfigModel.objects.get_or_create()

    applications_fall_potential = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=1,
        potential=True,
    ).order_by('priority').all()
    applications_spring_potential = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=2,
        potential=True,
    ).order_by('priority').all()
    applications_fall = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=1,
        potential=False,
    ).order_by('priority').all()
    applications_spring = StudentOnElective.objects.filter(
        student=user_id,
        kind__semester=2,
        potential=False,
    ).order_by('priority').all()
    fall_sum = logic.calc_sum_credit_units(person, 1)
    fall_min = person.student_data.student_group.min_credit_unit_fall
    spring_sum = logic.calc_sum_credit_units(person, 2)
    spring_min = person.student_data.student_group.min_credit_unit_spring
    context = {
        'applications_fall': applications_fall,
        'applications_spring': applications_spring,
        'applications_fall_potential': applications_fall_potential,
        'applications_spring_potential': applications_spring_potential,
        'fall_code_row': logic.generate_application_row(student=user_id, semester=1),
        'spring_code_row': logic.generate_application_row(student=user_id, semester=2),
        'credit_units_fall': {
            'max': person.student_data.student_group.max_credit_unit_fall,
            'min': fall_min,
            'sum': fall_sum,
            'is_too_few': int(fall_min > fall_sum),
        },
        'credit_units_potential_fall': {
            'sum': logic.calc_sum_credit_units(person, 1, True),
        },
        'credit_units_potential_spring': {
            'sum': logic.calc_sum_credit_units(person, 2, True),
        },
        'credit_units_spring': {
            'max': person.student_data.student_group.max_credit_unit_spring,
            'min': spring_min,
            'sum': spring_sum,
            'is_too_few': int(spring_min > spring_sum),
        },
        'show_google_form': config.show_google_form,
        'block_fall_applications': config.block_fall_applications,
        'block_spring_applications': config.block_spring_applications,
    }
    if config.show_google_form:
        context['google_form_url'] = config.google_form_url

    return render(request, 'electives/sort_electives.html', context)


@login_required
@require_GET
def restart_counter(request, **kwargs):
    if not request.user.is_superuser:
        return PermissionDenied

    statistic = Statistic()
    statistic.restart()
    return JsonResponse({'status': 'OK'})
