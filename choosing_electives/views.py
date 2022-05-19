from django.shortcuts import redirect, render


def home(request, **kwargs):
    return redirect('/electives/')


def help_page(request, **kwargs):
    return render(request, 'help.html')
