"""Elective models"""
from django.db import models


class Elective(models.Model):
    """
    Elective model

    str :: name  |  The name of this elective
    int :: credit_unit  |  The credit_unit of this elective
    """

    name: str = models.CharField(max_length=200)
    credit_unit: int = models.IntegerField(default=0)


class BigElective(Elective):
    """
    Course with both of theory and practice

    credit_unit = 4

    str :: name  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 4
        super().__init__(name, credit_unit, args, kwargs)


class SmallElective(Elective):
    """
    Course with only theory

    credit_unit = 3

    str :: name  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 3
        super().__init__(name, credit_unit, args, kwargs)


class Seminar(Elective):
    """
    Course with only practice

    credit_unit = 2

    str :: name  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 2
        super().__init__(name, credit_unit, args, kwargs)
