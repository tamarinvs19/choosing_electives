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


class YearOfEducation(Group):
    """One year students"""
    pass


class Curriculum(Group):
    """Students on same educational program"""
    pass
