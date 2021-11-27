"""Student groups models."""
from django.core.exceptions import ValidationError
from django.db import models

from .base_model import TimedModel


class Curriculum(TimedModel):
    """The educational program"""

    name: str = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if Curriculum.objects.filter(name=self.name).exists():
            raise ValidationError(
                'There is can be only one Curriculum instance with the same fields',
            )
        return super(Curriculum, self).save(*args, **kwargs)


class YearOfEducation(TimedModel):
    """One year education"""

    year: int = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return '{}st year'.format(self.year)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if YearOfEducation.objects.filter(year=self.year).exists():
            raise ValidationError('There is can be only one YearOfEducation instance with the same fields')
        return super(YearOfEducation, self).save(*args, **kwargs)


class StudentGroup(TimedModel):
    """One year and same educational program students"""

    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    course_value = models.ForeignKey(YearOfEducation, on_delete=models.CASCADE)

    students = models.ForeignKey(
        'Person',
        related_name='student_group',
        on_delete=models.SET_NULL,
        null=True,
    )

    min_credit_unit_autumn = models.PositiveSmallIntegerField()
    max_credit_unit_autumn = models.PositiveSmallIntegerField()
    min_credit_unit_spring = models.PositiveSmallIntegerField()
    max_credit_unit_spring = models.PositiveSmallIntegerField()

    min_number_of_exams_autumn = models.PositiveSmallIntegerField(default=1)
    max_number_of_exams_autumn = models.PositiveSmallIntegerField(default=1)
    min_number_of_exams_spring = models.PositiveSmallIntegerField(default=1)
    max_number_of_exams_spring = models.PositiveSmallIntegerField(default=1)

    max_light_credit_unit_autumn = models.PositiveSmallIntegerField(default=1, null=True)
    max_light_credit_unit_spring = models.PositiveSmallIntegerField(default=1, null=True)

    max_cs_courses_autumn = models.PositiveSmallIntegerField(default=1, null=True)
    max_cs_courses_spring = models.PositiveSmallIntegerField(default=1, null=True)

    def __str__(self):
        return '{0}: {1}'.format(str(self.curriculum), str(self.course_value))

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if StudentGroup.objects.filter(
                curriculum=self.curriculum,
                course_value=self.course_value,
        ).exists():
            raise ValidationError('There is can be only one StudentGroup instance with the same fields')
        return super(StudentGroup, self).save(*args, **kwargs)
