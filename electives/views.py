from django.shortcuts import render
from .controller import Controller


def open_elective_list(request, **kwargs):
    context = {'electives': Controller.get_all_electives()}
    return render(request, 'electives/elective_list.html', context)

