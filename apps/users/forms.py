from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from apps.groups.models import StudentGroup
from apps.users.models import Person


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label=_('First name'),
        max_length=100,
        initial='',
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=100,
        initial='',
    )
    email = forms.EmailField(
        label=_('Email'),
        initial='',
    )
    student_group = forms.ChoiceField(
        choices=[(group.id, group) for group in StudentGroup.objects.all()],
        initial=('-1', '-' * 20),
    )


class SignUpForm(UserCreationForm):

    first_name = forms.CharField(
        label=_('First name'),
        max_length=100,
        initial='',
    )
    last_name = forms.CharField(
        label=_('Last name'),
        max_length=100,
        initial='',
    )
    student_group = forms.ChoiceField(
        choices=[(group.id, group) for group in StudentGroup.objects.all()],
        initial=('-1', '-' * 20),
    )

    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'student_group')
