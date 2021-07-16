"""Person models"""
from django.contrib.auth.models import User


class Person(User):
    """Person model with sorting by the last name."""

    class Meta:
        proxy = True
        ordering = ('last_name', 'first_name')
