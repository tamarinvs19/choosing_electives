"""Group models"""
from django.contrib.auth.models import Group


class Administrations(Group):
    """Administration group"""
    pass


class Teachers(Group):
    """Teacher group"""
    pass


class Students(Group):
    """Student group"""
    pass
