from typing import cast

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.groups.models import Student
from apps.users.forms import ProfileForm, SignUpForm
from apps.users.models import Person, Invitation


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
    return render(request, 'users/personal_page.html', context)


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

            return redirect('/electives/users/{0}/'.format(student.id))

    else:
        initial = {
            'first_name': person.first_name,
            'last_name': person.last_name,
        }
        if ',' in person.email:
            emails = person.email[1:-1].split(',')
            if len(emails) > 0:
                initial['email'] = emails[0][1:-1]
        else:
            initial['email'] = person.email

        student, _ = Student.objects.get_or_create(
            person=person,
        )
        if student.student_group is not None:
            student_group = person.student_data.student_group
            initial['student_group'] = (student_group.id, student_group)

        form = ProfileForm(initial=initial)

    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def redirect_to_personal_page(request):
    user_id = request.user.id
    return redirect('/electives/users/{0}'.format(user_id))


def signup_view(request):
    invitation_key = request.GET.get('key', None)
    if invitation_key is None or not Invitation.objects.filter(
            invitation_key=invitation_key,
            deadline__gt=timezone.now(),
    ).exists():
        raise Http404

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            student_group_id = int(form.cleaned_data['student_group'])

            person = authenticate(
                username=username,
                password=raw_password,
            )

            Student.objects.create(
                person=person,
                student_group_id=student_group_id,
            )

            login(request, person)

            return redirect('account:personal_page', user_id=person.pk)
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form, 'key': invitation_key})
