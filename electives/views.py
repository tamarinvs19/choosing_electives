from django.shortcuts import render
from .controller import Controller
from .models import Elective


def open_elective_list(request, **kwargs):
    context = {'electives': Controller.get_all_electives()}
    return render(request, 'electives/elective_list.html', context)


def open_elective_page(request, elective_id, **kwargs):
    context = {'elective': Elective.objects.get(id=elective_id)}
    return render(request, 'electives/elective_page.html', context)

