"""Elective models"""
from django.db import models
from users.models import Person


class Elective(models.Model):
    """
    Elective model

    :name:        str           |  The name of this elective
    :credit_unit: int           |  The credit_unit of this elective
    :description: str           |  The description of this elective
    :students:    list[Pesron]  |  The list of students on this elective
    :teachers:    list[Pesron]  |  The list of teachers on this elective
    """

    name: str = models.CharField(max_length=200)
    credit_unit: int = models.IntegerField(default=0)
    description: str = models.TextField(default='')
    students = models.ManyToManyField(Person, related_name='student_list', through='StudentOnElective')
    teachers = models.ManyToManyField(Person, related_name='teaher_list', through='TeacherOnElective')


class BigElective(Elective):
    """
    Course with both of theory and practice

    credit_unit = 4

    :name: str  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 4
        super().__init__(name, credit_unit, args, kwargs)


class SmallElective(Elective):
    """
    Course with only theory

    credit_unit = 3

    :name: str  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 3
        super().__init__(name, credit_unit, args, kwargs)


class Seminar(Elective):
    """
    Course with only practice

    credit_unit = 2

    :name: str  |  The name of this elective
    """

    def __init__(self, name: str, *args, **kwargs):
        credit_unit: int = 2
        super().__init__(name, credit_unit, args, kwargs)


class StudentOnElective(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    is_necessary = models.BooleanField(default=False)


class TeacherOnElective(models.Model):
    teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)

