from django.shortcuts import render
from electives.models import Elective


def open_personal_page(request, user_id, **kwargs):
    context = {}
    return render(request, 'account/personal_page.html', context)


def open_sorting_page(request, user_id, **kwargs):
    context = {'electives': Elective.objects.all()}
    return render(request, 'account/sort_electives.html', context)

