from typing import cast

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from loguru import logger

from apps.electives.elective_statistic import Statistic
from apps.parsing.forms import ParsingForm, TableParsingForm

from apps.parsing import courses_table_parsing, table_parsing
from apps.parsing.models import ConfigModel


@login_required
def parsing_page(request, **kwargs):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = ParsingForm(request.POST)
        if form.is_valid():
            config, _ = ConfigModel.objects.get_or_create()
            config.google_form_url = form.cleaned_data['google_form_url']
            config.block_fall = form.cleaned_data['block_fall']
            config.russian_url = form.cleaned_data['russian_url']
            config.english_url = form.cleaned_data['english_url']
            config.save()

            courses_table_parsing.run_parsing()

            statistic = Statistic()
            statistic.restart()

            return redirect('/electives/admin/')

    else:
        config, _ = ConfigModel.objects.get_or_create()
        initial = {
            'russian_url': config.russian_url,
            'english_url': config.english_url,
            'google_form_url': config.google_form_url,
            'block_fall': config.block_fall,
        }
        form = ParsingForm(initial=initial)

    return render(request, 'parsing/parsing_page.html', {'form': form})


@login_required
def table_parsing_page(request, **kwargs):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        form = TableParsingForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['create_thematic_keys']:
                table_parsing.create_short_thematic_keys()
            table = form.cleaned_data['table']
            data = [line.decode() for line in table]
            report = table_parsing.parse_elective_table(data)

            return render(
                request,
                'parsing/report_page.html',
                {'report': report},
            )

    else:
        form = TableParsingForm()

    return render(request, 'parsing/table_parsing_page.html', {'form': form})


@login_required
def parsing_report_page(request, **kwargs):
    if not request.user.is_superuser:
        raise PermissionDenied
