"""Person models"""
from django.contrib.auth.models import User


class Person(User):
    """Person model with sorting by the second name."""

    class Meta:
        proxy = True
        ordering = ('second_name', 'first_name')
