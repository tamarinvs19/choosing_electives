from django.shortcuts import redirect


def home(request, **kwargs):
    return redirect('/electives/')
