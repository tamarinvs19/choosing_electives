
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from electives.models import Elective, StudentOnElective


@login_required
def open_personal_page(request, **kwargs):
    context = {}
    return render(request, 'account/personal_page.html', context)


@login_required
def open_sorting_page(request, user_id, **kwargs):
    applications = StudentOnElective.objects.filter(student=user_id).all()
    context = {
        'applications': applications
    }
    return render(request, 'account/sort_electives.html', context)

