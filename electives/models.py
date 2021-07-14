"""Elective models"""
from django.db import models


class Elective(models.Model):
    """Elective model"""
    pass


class BigElective(Elective):
    """Course with both of theory and practice"""
    pass


class SmallElective(Elective):
    """Course with only theory"""
    pass


class Seminar(Elective):
    """Course with only practice"""
    pass
