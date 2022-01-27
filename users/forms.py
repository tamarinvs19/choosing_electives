from django import forms

from groups.models import StudentGroup


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label='First name',
        max_length=100,
        initial='',
    )
    last_name = forms.CharField(
        label='Last name',
        max_length=100,
        initial='',
    )
    email = forms.EmailField(
        label='Email',
        initial='',
    )
    student_group = forms.ChoiceField(
        choices=[(group.id, group) for group in StudentGroup.objects.all()],
        initial=('-1', '-' * 20),
    )
