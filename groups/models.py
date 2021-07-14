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


class TheThirdYear(Group):
    """The third year students"""
    pass


class TheFourthYear(Group):
    """The fourth year students"""
    pass


class Mathematics(Group):
    """Students on Mathematics program"""
    pass


class DataScience(Group):
    """Students on DataScience program"""
    pass


class ModernProgramming(Group):
    """Students on ModernProgramming (SP) program"""
    pass
