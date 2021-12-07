"""Elective models"""
from typing import Optional, Any, Dict, Tuple

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F

from groups.models import StudentGroup
from users.models import Person


KIND_NAMES: dict[int, str] = {
    2: 'Семинар',
    3: 'Малый',
    4: 'Большой',
}

ENGLISH_KIND_NAMES: dict[int, str] = {
    2: 'Seminar',
    3: 'Small',
    4: 'Large',
}

LANG_NAMES: dict[str, str] = {
    'ru': 'на русском',
    'en': 'на английском',
}

ENGLISH_LANG_NAMES: dict[str, str] = {
    'ru': 'in Russian',
    'en': 'in English',
}

SEMESTERS: dict[int, str] = {
    1: 'осенний',
    2: 'весенний',
}
ENGLISH_SEMESTERS: dict[int, str] = {
    1: 'fall',
    2: 'spring',
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

    def __repr__(self) -> str:
        return '<ElectiveKind: {0}>'.format(self.short_name)

    def __str__(self) -> str:
        if self.language == 'ru':
            return '{kind} {lang} {semester}'.format(
                    kind=KIND_NAMES[self.credit_units],
                    lang=LANG_NAMES[self.language],
                    semester=SEMESTERS[self.semester],
            )
        else:
            return '{kind} {lang} {semester}'.format(
                kind=ENGLISH_KIND_NAMES[self.credit_units],
                lang=ENGLISH_LANG_NAMES[self.language],
                semester=ENGLISH_SEMESTERS[self.semester],
            )

    @admin.display(description='Title')
    def show_name(self) -> str:
        """Generate the string form for admin site"""
        return str(self)

    @property
    def semester_english_name(self) -> str:
        return ENGLISH_SEMESTERS[self.semester]

    @property
    def is_seminar(self) -> bool:
        """Return True if it is a seminar"""
        return self.credit_units == 2

    @property
    def long_name(self) -> str:
        """Generate the full string form"""
        return str(self)

    @property
    def short_name(self) -> str:
        """Generate the short string form"""
        semester = {1: 'F', 2: 'S'}[self.semester]
        if self.credit_units == 2:
            return '{lang}s{semester}'.format(
                lang=self.language, semester=semester,
            )
        elif self.credit_units == 3:
            return '{lang}1{semester}'.format(
                lang=self.language, semester=semester,
            )
        elif self.credit_units == 4:
            return '{lang}2{semester}'.format(
                lang=self.language, semester=semester,
            )

    @property
    def middle_name(self) -> str:
        """Generate the long name without semester"""
        if self.language == 'ru':
            return '{kind} {lang}'.format(
                kind=KIND_NAMES[self.credit_units],
                lang=LANG_NAMES[self.language],
            )
        else:
            return '{kind} {lang}'.format(
                kind=ENGLISH_KIND_NAMES[self.credit_units],
                lang=ENGLISH_LANG_NAMES[self.language],
            )

    @property
    def credit_units_name(self) -> str:
        return KIND_NAMES[self.credit_units]

    @property
    def credit_units_english_name(self) -> str:
        return ENGLISH_KIND_NAMES[self.credit_units]


class ElectiveThematic(models.Model):
    """
    Elective thematic model
    """

    name = models.CharField(max_length=200, unique=True)
    english_name = models.CharField(max_length=200, unique=True)

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
    :english_name:         |  The english name of this elective
    :credit_unit:          |  The credit_unit of this elective
    :description:          |  The description of this elective
    :english_description:  |  The english description of this elective
    :max_number_students:  |  Maximum of number of students on this elective
    :min_number_students:  |  Minimum of number of students on this elective
    :thematic:             |  ForeignKey with thematic of this elective
    :kinds:                |  ManyToManyField with possible kinds of this elective
    :students:             |  ManyToManyField with students on this elective
    :text_teachers:        |  List of teacher names
    """

    name = models.CharField(max_length=200)
    english_name = models.CharField(max_length=200, null=True, default='')
    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, default='')
    english_description = models.CharField(max_length=200, null=True, default='')
    max_number_students = models.PositiveIntegerField(default=255)
    min_number_students = models.PositiveIntegerField(default=3)
    thematic = models.ForeignKey(ElectiveThematic, null=True, on_delete=models.SET_NULL)
    kinds = models.ManyToManyField(ElectiveKind, related_name='elective_kinds', through='KindOfElective')
    students = models.ManyToManyField(Person, related_name='student_list', through='StudentOnElective')
    text_teachers = models.CharField(max_length=100, default='', null=True)

    def __repr__(self) -> str:
        return '<Elective: {0}>'.format(self.codename)

    def __str__(self) -> str:
        return '<Elective: {0}>'.format(self.codename)

    @property
    def has_russian_kind(self) -> bool:
        return self.kinds.filter(language='ru').exists()

    @property
    def has_english_kind(self) -> bool:
        return self.kinds.filter(language='en').exists()

    @property
    def has_not_fall(self) -> bool:
        return not self.kinds.filter(semester=1).exists()

    @property
    def has_fall(self) -> bool:
        return self.kinds.filter(semester=1).exists()

    @property
    def has_not_spring(self) -> bool:
        return not self.kinds.filter(semester=2).exists()

    @property
    def has_spring(self) -> bool:
        return self.kinds.filter(semester=2).exists()

    @property
    def translated_name(self) -> str:
        if self.has_english_kind:
            return self.english_name
        return self.name

    @property
    def text_kinds(self) -> list[(str, str, str)]:
        """Generate the list of kinds as tuple (short_form, long_form, semester)."""
        return [(kind.short_name, kind.long_name, kind.semester) for kind in self.kinds.all()]

    @property
    def text_kinds_with_ids(self) -> list[(str, int)]:
        """Generate the list of kinds as tuple (long_form, id)."""
        return [(kind.long_name, kind.id) for kind in self.kinds.all()]


class KindOfElective(models.Model):
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE)


class StudentOnElective(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE, null=True, default=None)
    with_examination = models.BooleanField(default=True)
    attached = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0)

    def delete(self, using: Any = None, keep_parents: bool = False) -> Tuple[int, Dict[str, int]]:
        StudentOnElective.objects.filter(
            student=self.student,
            attached=self.attached,
            kind__semester=self.kind.semester,
            priority__gt=self.priority,
        ).update(priority=F('priority') - 1)

        return super().delete(using, keep_parents)

    def __str__(self):
        return 'StudentOnElective - {0}: {1} {2}, {3}, {4}'.format(
            self.student.username,
            self.elective.codename,
            self.kind.short_name,
            self.attached,
            self.priority,
        )

    @property
    def credit_units(self) -> int:
        if self.kind.credit_units == 2:
            return 2
        elif self.with_examination:
            return self.kind.credit_units
        else:
            return self.kind.credit_units - 1

    @property
    def short_name(self) -> str:
        """Generate the short string form without semester letter"""
        kind_mark = {2: 's', 3: '1', 4: '2'}
        exam = '' if self.with_examination else '-'
        return '{elective}{exam}:{lang}{kind}'.format(
            elective=self.elective.codename,
            lang=self.kind.language,
            kind=kind_mark[self.kind.credit_units],
            exam=exam,
        )

    @property
    def is_seminar(self) -> bool:
        return self.kind.is_seminar

    @property
    def text_kinds_with_ids(self) -> list[tuple[str, int, str]]:
        """Generate the list of kinds as tuple (long_form, id, semester)."""
        return [
            (kind.middle_name, kind.id, ENGLISH_SEMESTERS[kind.semester])
            for kind in self.elective.kinds.all()
        ]


class MandatoryThematicInStudentGroup(models.Model):
    thematic = models.ForeignKey(ElectiveThematic, on_delete=models.CASCADE, related_name='mandatory_thematics')
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name='mandatory_thematics')
