from typing import cast

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from loguru import logger

from apps.electives.elective_statistic import Statistic
from apps.parsing.forms import ParsingForm

from apps.parsing import courses_table_parsing
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

            courses_table_parsing.create_default_kinds()
            courses_table_parsing.main_programs()
            courses_table_parsing.main_electives()
            courses_table_parsing.create_default_mandatory_thematics()

            statistic = Statistic()
            statistic.restart()

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
