"""Person models"""
import random
import string

from django.contrib.sites.models import Site
from django.db import models
from django.contrib.auth.models import User


class Person(User):
    """Person model with sorting by the last name."""

    def __str__(self):
        if self.first_name and self.last_name:
            return '{0} {1}'.format(self.first_name, self.last_name)
        else:
            return self.username

    class Meta:
        proxy = True
        ordering = ('last_name', 'first_name')


def generate_invitation_key(length: int = 40) -> str:
    characters = (
        string.ascii_letters
        + string.digits
        + '-._~'
    )
    return ''.join(random.choices(characters, k=length))


class Invitation(models.Model):
    invitation_key = models.CharField(max_length=100, null=True, blank=True)
    deadline = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        if self.invitation_key is None:
            self.invitation_key = generate_invitation_key()
        super().save(force_insert, force_update, using, update_fields)

    @property
    def link(self):
        current_site = Site.objects.get_current()
        return 'https://{domen}/electives/users/invite/?key={key}'.format(
            domen=current_site,
            key=self.invitation_key,
        )
