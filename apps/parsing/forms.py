from django import forms


class ParsingForm(forms.Form):
    russian_url = forms.URLField(
        label='Russian URL',
        initial='',
    )
    english_url = forms.URLField(
        label='English URL',
        initial='',
    )
    block_fall = forms.BooleanField(
        label='Block fall',
        initial=False,
        required=False,
    )
    google_form_url = forms.URLField(
        label='Google form URL',
        initial='',
    )
