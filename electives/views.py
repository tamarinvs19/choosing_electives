from django.shortcuts import render
from .models import Elective, ElectiveThematic


def open_elective_list(request, **kwargs):
    context = {'electives': Elective.objects.all(), 'thematics': ElectiveThematic.objects.all()}
    return render(request, 'electives/elective_list.html', context)


def open_elective_page(request, elective_id, **kwargs):
    context = {'elective': Elective.objects.get(id=elective_id)}
    return render(request, 'electives/elective_page.html', context)
