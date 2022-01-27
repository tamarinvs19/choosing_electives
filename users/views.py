from typing import cast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest

from loguru import logger

from groups.models import StudentGroup, Student
from users.forms import ProfileForm
from users.models import Person


@login_required
def open_personal_page(request, **kwargs):
    student = cast(Person, request.user)
    context = {
        'user': student,
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


@login_required
def profile_edit(request, **kwargs):
    person = cast(Person, request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            person.first_name = form.cleaned_data['first_name']
            person.last_name = form.cleaned_data['last_name']
            person.email = form.cleaned_data['email'],
            person.save()

            student, _ = Student.objects.get_or_create(
                person=person,
            )
            student.student_group_id = int(form.cleaned_data['student_group'])
            student.save()

            logger.debug(student)
            return redirect('/electives/users/{0}/'.format(student.id))

    else:
        initial = {
            'first_name': person.first_name,
            'last_name': person.last_name,
        }
        emails = person.email[1:-1].split(',')
        if len(emails) > 0:
            initial['email'] = emails[0][1:-1]

        if Student.objects.filter(person=person).exists():
            student_group = person.student_data.student_group
            initial['student_group'] = (student_group.id, student_group)

        form = ProfileForm(initial=initial)

    return render(request, 'electives/profile_edit.html', {'form': form})
