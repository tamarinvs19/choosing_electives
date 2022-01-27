"""Group models"""
from django.core.exceptions import ValidationError
from django.db import models

from users.models import Person


class Curriculum(models.Model):
    """The educational program"""
    
    name: str = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if Curriculum.objects.filter(name=self.name).exists():
            raise ValidationError('There is can be only one Curriculum instance with the same fields')
        return super(Curriculum, self).save(*args, **kwargs)


class YearOfEducation(models.Model):
    """One year education"""

    year: int = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return '{}st year'.format(self.year)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if YearOfEducation.objects.filter(year=self.year).exists():
            raise ValidationError('There is can be only one YearOfEducation instance with the same fields')
        return super(YearOfEducation, self).save(*args, **kwargs)


class StudentGroup(models.Model):
    """One year and same educational program students"""

    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    course_value = models.ForeignKey(YearOfEducation, on_delete=models.CASCADE)

    min_credit_unit_fall = models.PositiveSmallIntegerField(default=1)
    max_credit_unit_fall = models.PositiveSmallIntegerField(default=1)
    min_credit_unit_spring = models.PositiveSmallIntegerField(default=1)
    max_credit_unit_spring = models.PositiveSmallIntegerField(default=1)

    min_number_of_exams_fall = models.PositiveSmallIntegerField(default=None, null=True)
    max_number_of_exams_fall = models.PositiveSmallIntegerField(default=None, null=True)
    min_number_of_exams_spring = models.PositiveSmallIntegerField(default=None, null=True)
    max_number_of_exams_spring = models.PositiveSmallIntegerField(default=None, null=True)

    max_light_credit_unit_fall = models.PositiveSmallIntegerField(default=None, null=True)
    max_light_credit_unit_spring = models.PositiveSmallIntegerField(default=None, null=True)

    max_cs_courses_fall = models.PositiveSmallIntegerField(default=None, null=True)
    max_cs_courses_spring = models.PositiveSmallIntegerField(default=None, null=True)

    def __str__(self):
        return '{0}: {1}'.format(str(self.curriculum), str(self.course_value))

    def __le__(self, other) -> bool:
        return str(self) < str(other)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        existing_groups = StudentGroup.objects.filter(
                curriculum=self.curriculum,
                course_value=self.course_value,
        )
        if existing_groups.exists() and not (len(existing_groups) == 1 and existing_groups[0].id == self.id):
            raise ValidationError('There is can be only one StudentGroup instance with the same fields')
        return super(StudentGroup, self).save(*args, **kwargs)


class Student(models.Model):
    person = models.OneToOneField(
        Person,
        related_name='student_data',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    student_group = models.ForeignKey(
        StudentGroup,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='students',
    )

