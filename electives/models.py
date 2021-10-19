"""Elective models"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models

from groups.models import StudentGroup
from users.models import Person


KIND_NAMES: dict[int, str] = {
    2: 'Семинар',
    3: 'Малый',
    4: 'Большой',
}

LANG_NAMES: dict[str, str] = {
    'ru': 'на русском',
    'en': 'на английском',
}

SEMESTERS: dict[int: str] = {
    1: 'осенний',
    2: 'весенний',
}


class ElectiveKind(models.Model):
    """Kind of elective: big/small/seminar + language"""

    credit_units: int = models.PositiveSmallIntegerField(choices=KIND_NAMES.items(), default=4)
    language: str = models.CharField(max_length=2, choices=LANG_NAMES.items(), default='ru')
    semester: int = models.PositiveSmallIntegerField(choices=SEMESTERS.items(), default=1)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if ElectiveKind.objects.filter(
                credit_units=self.credit_units,
                language=self.language,
                semester=self.semester
                ).exists():
            raise ValidationError('There is can be only one ElectiveKind instance with the same fields')
        return super(ElectiveKind, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return '{kind} {lang} {semester}'.format(
                kind=KIND_NAMES[self.credit_units],
                lang=LANG_NAMES[self.language],
                semester=SEMESTERS[self.semester],
        )

    @admin.display(description='Title')
    def show_name(self) -> str:
        """Generate the string form for admin site"""
        return str(self)

    @property
    def short_name(self) -> str:
        """Generate the short string form"""
        if self.credit_units == 2:
            return '{lang}s-{semester}'.format(
                lang=self.language, semester=self.semester,
            )
        elif self.credit_units == 3:
            return '{lang}1-{semester}'.format(
                lang=self.language, semester=self.semester,
            )
        elif self.credit_units == 4:
            return '{lang}2-{semester}'.format(
                lang=self.language, semester=self.semester,
            )


class ElectiveThematic(models.Model):
    """
    Elective thematic model
    """

    name = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        return str(self.name)

    @admin.display(description='Name')
    def show_name(self) -> str:
        """Generate the string form for admin site"""
        return str(self)


class Elective(models.Model):
    """
    Elective model

    :name:                 |  The name of this elective
    :credit_unit:          |  The credit_unit of this elective
    :description:          |  The description of this elective
    :max_number_students:  |  Maximum of number of students on this elective
    :min_number_students:  |  Minimum of number of students on this elective
    :thematic:             |  ForeignKey with thematic of this elective
    :kinds:                |  ManyToManyField with possible kinds of this elective
    :students:             |  ManyToManyField with students on this elective
    :teachers:             |  ManyToManyField with teachers on this elective
    """

    name = models.CharField(max_length=200)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='')
    max_number_students = models.PositiveIntegerField(default=255)
    min_number_students = models.PositiveIntegerField(default=3)
    thematic = models.ForeignKey(ElectiveThematic, null=True, on_delete=models.SET_NULL)
    kinds = models.ManyToManyField(ElectiveKind, related_name='elective_kinds', through='KindOfElective')
    students = models.ManyToManyField(Person, related_name='student_list', through='StudentOnElective')
    teachers = models.ManyToManyField(Person, related_name='teacher_list', through='TeacherOnElective')
    text_teachers = models.CharField(max_length=100, default='', null=True)

    @property
    def text_teacher(self) -> str:
        """Generate the teacher's list in the text format."""
        if len(self.teachers.all()) > 0:
            return ', '.join(map(lambda t: str(t), self.teachers.all()))
        elif self.text_teachers is not None:
            return self.text_teachers
        else:
            return 'Не определен'

    @property
    def text_kinds(self) -> list[(str, str, str)]:
        """Generate the list of kinds as pairs (short_form, long_form, semester)."""
        return [(kind.short_name, kind.show_name, kind.semester) for kind in self.kinds.all()]


class KindOfElective(models.Model):
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE)


class StudentOnElective(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    with_examination = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)


class TeacherOnElective(models.Model):
    teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)


class MandatoryElectiveInStudentGroup(models.Model):
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
