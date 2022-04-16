"""Elective models"""
from typing import Any, Dict, Tuple

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F

from model_utils import FieldTracker

from apps.groups.models import StudentGroup
from apps.users.models import Person


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


class ExamPossibility(models.TextChoices):
    ONLY_WITH_EXAM = '+', 'Only with the exam'
    ONLY_WITHOUT_EXAM = '-', 'Only without the exam'
    DEFAULT = '+-', 'With the exam or without the exam'


class CreditUnitsKind(models.Model):
    credit_units = models.PositiveSmallIntegerField(default=4)
    russian_name = models.CharField(max_length=50)
    english_name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=2)  

    default_exam_possibility = models.CharField(
        max_length=2,
        choices=ExamPossibility.choices,
        default=ExamPossibility.DEFAULT,
    )

    def __str__(self):
        return '<CreditUnitsKind: name={0}, credit_units={1}>'.format(
            self.russian_name,
            self.credit_units,
        )

    def get_name_by_language(self, language: str) -> str:
        return self.russian_name if language == 'ru' else self.english_name


class ElectiveKind(models.Model):
    credit_units_kind = models.ForeignKey(
        'CreditUnitsKind',
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )
    language = models.CharField(max_length=2, choices=LANG_NAMES.items(), default='ru')
    semester = models.PositiveSmallIntegerField(choices=SEMESTERS.items(), default=1)

    def save(self, *args, **kwargs) -> None:
        """Save the current instance only if there are not the same."""
        if ElectiveKind.objects.filter(
                credit_units_kind=self.credit_units_kind,
                language=self.language,
                semester=self.semester,
        ).exists():
            raise ValidationError('There is can be only one ElectiveKind instance with the same fields')
        return super(ElectiveKind, self).save(*args, **kwargs)

    def __repr__(self) -> str:
        return '<ElectiveKind: {0}>'.format(self.short_name)

    def __str__(self) -> str:
        if self.language == 'ru':
            return '{kind} {lang} {semester}'.format(
                    kind=self.credit_units_kind.russian_name,
                    lang=LANG_NAMES[self.language],
                    semester=SEMESTERS[self.semester],
            )
        else:
            return '{kind} {lang} {semester}'.format(
                kind=self.credit_units_kind.english_name,
                lang=ENGLISH_LANG_NAMES[self.language],
                semester=ENGLISH_SEMESTERS[self.semester],
            )

    @admin.display(description='Title')
    def show_name(self) -> str:
        """Generate the string form for admin site"""
        return str(self)

    @property
    def credit_units(self) -> int:
        return self.credit_units_kind.credit_units

    @property
    def semester_english_name(self) -> str:
        return ENGLISH_SEMESTERS[self.semester]

    @property
    def long_name(self) -> str:
        """Generate the full string form"""
        return str(self)

    @property
    def short_name(self) -> str:
        """Generate the short string form"""
        semester = {1: 'F', 2: 'S'}[self.semester]
        return '{lang}{short_kind}{semester}'.format(
            lang=self.language,
            short_kind=self.credit_units_kind.short_name,
            semester=semester,
        )

    @property
    def middle_name(self) -> str:
        """Generate the long name without semester"""
        if self.language == 'ru':
            return '{kind} {lang}'.format(
                kind=self.credit_units_kind.russian_name,
                lang=LANG_NAMES[self.language],
            )
        else:
            return '{kind} {lang}'.format(
                kind=self.credit_units_kind.english_name,
                lang=ENGLISH_LANG_NAMES[self.language],
            )

    @property
    def credit_units_name(self) -> str:
        return self.credit_units_kind.russian_name

    @property
    def credit_units_english_name(self) -> str:
        return self.credit_units_kind.english_name


class ElectiveThematic(models.Model):
    """
    Elective thematic model
    """

    name = models.CharField(max_length=200, unique=True)
    english_name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=10, default=None, null=True)

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
    :description:          |  The description of this elective
    :english_description:  |  The english description of this elective
    :max_number_students:  |  Maximum of number of students on this elective
    :min_number_students:  |  Minimum of number of students on this elective
    :thematic:             |  ForeignKey with thematic of this elective
    :kinds:                |  ManyToManyField with possible kinds of this elective
    :students:             |  ManyToManyField with students on this elective
    :text_teachers:        |  List of teacher names
    """

    name = models.CharField(max_length=200, null=True, default='', blank=True)
    english_name = models.CharField(max_length=200, null=True, default='', blank=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, null=True, default='', blank=True)
    english_description = models.CharField(max_length=200, null=True, default='', blank=True)
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
        return not self.has_fall

    @property
    def has_fall(self) -> bool:
        return self.kinds.filter(semester=1).exists()

    @property
    def has_not_spring(self) -> bool:
        return not self.has_spring

    @property
    def has_spring(self) -> bool:
        return self.kinds.filter(semester=2).exists()

    @property
    def translated_name(self) -> str:
        if self.has_english_kind:
            if len(self.english_name) > 0:
                return self.english_name
        return self.name

    @property
    def text_kinds(self) -> list[Tuple[str, str, str]]:
        """Generate the list of kinds as tuple (short_form, long_form, semester)."""
        return [(kind.short_name, kind.long_name, kind.semester) for kind in self.kinds.all()]

    @property
    def text_kinds_with_ids(self) -> list[Tuple[str, int]]:
        """Generate the list of kinds as tuple (long_form, id)."""
        return [(kind.long_name, kind.id) for kind in self.kinds.all()]


class KindOfElective(models.Model):
    elective = models.ForeignKey(
        Elective,
        on_delete=models.CASCADE,
        related_name='kind_of_elective',
    )
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE)
    exam_possibility = models.CharField(
        max_length=2,
        choices=ExamPossibility.choices,
        default=ExamPossibility.DEFAULT,
    )

    @property
    def exam_is_possible(self):
        return not self.only_without_exam

    @property
    def only_with_exam(self):
        return self.exam_possibility == ExamPossibility.ONLY_WITH_EXAM

    @property
    def only_without_exam(self):
        return self.exam_possibility == ExamPossibility.ONLY_WITHOUT_EXAM

    @property
    def changing_exam_is_possible(self):
        return self.exam_possibility == ExamPossibility.DEFAULT


class StudentOnElective(models.Model):
    student = models.ForeignKey(Person, on_delete=models.CASCADE)
    elective = models.ForeignKey(Elective, on_delete=models.CASCADE)
    kind = models.ForeignKey(ElectiveKind, on_delete=models.CASCADE, null=True, default=None)
    with_examination = models.BooleanField(default=True)
    attached = models.BooleanField(default=False)
    priority = models.PositiveIntegerField(default=0)

    tracker = FieldTracker(fields=['kind', 'attached'])

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
    def kind_of_elective(self):
        return KindOfElective.objects.get(
            elective=self.elective,
            kind=self.kind,
        )

    @property
    def credit_units(self) -> int:
        if self.with_examination or self.kind_of_elective.only_without_exam:
            return self.kind.credit_units
        else:
            return self.kind.credit_units - 1

    @property
    def short_name(self) -> str:
        """Generate the short string form without semester letter"""
        exam = '' if self.with_examination else '-'
        return '{elective}{exam}:{lang}{kind}'.format(
            elective=self.elective.codename,
            lang=self.kind.language,
            kind=self.kind.credit_units_kind.short_name,
            exam=exam,
        )

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
