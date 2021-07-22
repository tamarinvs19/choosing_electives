"""Group models"""
from django.db import models


class Curriculum(models.Model):
    """The educational program"""
    
    name: str = models.CharField(max_length=100, default='')


class YearOfEducation(models.Model):
    """One year education"""

    year: int = models.PositiveSmallIntegerField(default=1)


class StudentGroup(models.Model):
    """One year and same educational program students"""

    curriculum: Curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    course_value: YearOfEducation = models.ForeignKey(YearOfEducation, on_delete=models.CASCADE)
    min_credit_unit_autumn = models.PositiveSmallIntegerField()
    max_credit_unit_autumn = models.PositiveSmallIntegerField()
    min_credit_unit_spring = models.PositiveSmallIntegerField()
    max_credit_unit_spring = models.PositiveSmallIntegerField()
    min_number_of_exams_autumn = models.SmallIntegerField(default=1)
    min_number_of_exams_spring = models.SmallIntegerField(default=1)
