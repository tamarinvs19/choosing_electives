"""Group models"""
from django.contrib.auth.models import Group


class YearOfEducation(Group):
    """One year students"""
    pass


class Curriculum(Group):
    """Students on same educational program"""
    pass
