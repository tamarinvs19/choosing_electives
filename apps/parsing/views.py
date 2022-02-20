from typing import cast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from loguru import logger

from constance import config as cfg

from apps.parsing.forms import ParsingForm
from apps.users.models import Person

from apps.parsing import courses_table_parsing


@login_required
def parsing_page(request, **kwargs):
    person = cast(Person, request.user)

    if request.method == 'POST':
        form = ParsingForm(request.POST)
        if form.is_valid():
            cfg.RUSSIAN_URL = form.cleaned_data['russian_url']
            cfg.ENGLISH_URL = form.cleaned_data['english_url']
            cfg.GOOGLE_FORM_URL = form.cleaned_data['google_form_url']
            cfg.BLOCK_FALL = form.cleaned_data['block_fall']

            courses_table_parsing.create_default_kinds()
            courses_table_parsing.main_programs()
            courses_table_parsing.main_electives()
            courses_table_parsing.create_default_mandatory_thematics()

    else:
        initial = {
            'russian_url': cfg.RUSSIAN_URL,
            'english_url': cfg.ENGLISH_URL,
            'google_form_url': cfg.GOOGLE_FORM_URL,
            'block_fall': cfg.BLOCK_FALL,
        }
        form = ParsingForm(initial=initial)

    return render(request, 'parsing/parsing_page.html', {'form': form})
