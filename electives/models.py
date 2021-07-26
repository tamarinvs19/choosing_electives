"""Elective models"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from users.models import Person


KIND_NAMES: dict[int, str] = {
    2: 'Семинар',
    3: 'Малый',
    4: 'Большой',
}

LANG_NAMES: dict[str, str] = {
    'ru': 'по-русски',
    'en': 'по-английски',
}


class ElectiveKind(models.Model):
    """Kind of elective: big/small/seminar + language"""

    credit_units: int = models.PositiveSmallIntegerField(choices=KIND_NAMES.items())
    language: str = models.CharField(max_length=2, choices=LANG_NAMES.items())

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if ElectiveKind.objects.filter(credit_units=self.credit_units, language=self.language).exists():
            raise ValidationError('There is can be only one ElectiveKind instance with the same fields')
        return super(ElectiveKind, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return '{kind} {lang}'.format(
                kind=KIND_NAMES[self.credit_units],
                lang=LANG_NAMES[self.language],
        )

    @admin.display(description='Title')
    def show_name(self) -> str:
        """Generate the string form for admin site"""
        return str(self)

    @property
    def short_name(self) -> str:
        """Generate the short string form"""
        if self.credit_units == 2:
            return '{lang}s'.format(lang=self.language)
        elif self.credit_units == 3:
            return '{lang}1'.format(lang=self.language)
        elif self.credit_units == 4:
            return '{lang}2'.format(lang=self.language)


class Elective(models.Model):
    """
    Elective model

    :name:        str           |  The name of this elective
    :credit_unit: int           |  The credit_unit of this elective
    :description: str           |  The description of this elective
    :max_number_students: int   |  Maximum of number of students on this elective
    :min_number_students: int   |  Minimum of number of students on this elective
    :students:    list[Person]  |  The list of students on this elective
    :teachers:    list[Person]  |  The list of teachers on this elective
    """

    name: str = models.CharField(max_length=200)
    codename: str = models.CharField(max_length=100, unique=True)
    description: str = models.TextField(default='')
    max_number_students: int = models.PositiveIntegerField(default=10)
    min_number_students: int = models.PositiveIntegerField(default=3)
    kinds = models.ManyToManyField(ElectiveKind, related_name='elective_kinds', through='KindOfElective')
    students = models.ManyToManyField(Person, related_name='student_list', through='StudentOnElective')
    teachers = models.ManyToManyField(Person, related_name='teacher_list', through='TeacherOnElective')

    @property
    def text_teacher(self) -> str:
        """Generate the teacher`s list in the text format."""
        if len(self.teachers.all()) > 0:
            return ', '.join(map(lambda t: str(t), self.teachers.all()))
        else:
            return 'Не определен'

    @property
    def text_kinds(self) -> list[(str, str)]:
        """Generate the list of kinds as pairs (short_form, long_form)."""
        return [(kind.short_name, kind.show_name) for kind in self.kinds.all()]


class KindOfElective(models.Model):
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE)


class StudentOnElective(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    is_necessary = models.BooleanField(default=False)
    with_examination = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)


class TeacherOnElective(models.Model):
    teacher = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)

