from collections import Counter
from dataclasses import dataclass
from typing import Optional
import datetime as dt

from django.db.models import QuerySet
from loguru import logger

from apps.electives.models import ElectiveThematic, Elective, ElectiveKind
from apps.groups.models import Student
from apps.parsing.models import ConfigModel


@dataclass
class BaseNode:
    def __init__(self, items, *args, **kwargs):
        self.items = items
        self.properties = {}

    def __getitem__(self, item):
        return self.items[item]

    def generate_view(self, student_id: int):
        view = (
            self.properties, [
                inner_item.generate_view(student_id)
                for inner_item in self.items.values()
            ]
        )
        return view

    def student_count(self, semester: int, potential: bool = False) -> int:
        return sum(
            inner_item.student_count(semester, potential)
            for inner_item in self.items.values()
        )


@dataclass
class _MaybeCounter(BaseNode):
    def __init__(self, elective: Elective, kind: ElectiveKind, potential: bool):
        items = Counter(
            sone.student.id
            for sone in elective.studentonelective_set.filter(
                kind=kind,
                potential=potential,
            )
        )
        super().__init__(items)

    def add_student(self, student_id: int):
        self.items[student_id] += 1

    def remove_student(self, student_id: int):
        if student_id in self.items:
            self.items[student_id] -= 1
            if self.items[student_id] == 0:
                self.items.pop(student_id, None)

    def remove_student_all(self, student_id: int):
        self.items.pop(student_id, None)

    def generate_view(self, student_id: int):
        ids = self.items.keys()
        return len(ids), student_id in ids


@dataclass
class _ApplicationCounter(BaseNode):
    def __init__(self, elective: Elective, kind: ElectiveKind):
        items = {
            True: _MaybeCounter(elective, kind, True),
            False: _MaybeCounter(elective, kind, False),
        }
        super().__init__(items)
        self.properties = {
            'pk': kind.pk,
            'short_name': kind.short_name,
            'long_name': kind.long_name,
            'semester': kind.semester,
            'credit_units_name': kind.credit_units_name,
            'credit_units_english_name': kind.credit_units_english_name,
        }

    def student_count(self, _: int, potential: bool = False) -> int:
        return len(self.items[potential].items.keys())

    def remove_student_all(self, student_id: int) -> None:
        for potential_counter in self.items.values():
            potential_counter.remove_student_all(student_id)

    def generate_view(self, student_id: int):
        view = (
            self.properties, {
                item: inner_item.generate_view(student_id)
                for item, inner_item in self.items.items()
            }
        )
        return view


@dataclass
class _Semester(BaseNode):
    def __init__(self, elective: Elective, kinds: QuerySet[ElectiveKind], semester: int):
        kinds = {
            kind_semester: _ApplicationCounter(elective, kind_semester)
            for kind_semester in kinds
        }
        super().__init__(kinds)
        self.properties = semester


@dataclass
class _Language(BaseNode):
    def __init__(self, elective: Elective, kinds: QuerySet[ElectiveKind], language: str):
        kind_semesters = set(kinds.values_list('semester', flat=True))
        semesters = {
            int(semester): _Semester(
                elective,
                kinds.filter(semester=semester),
                int(semester),
            )
            for semester in kind_semesters
        }
        super().__init__(semesters)
        self.properties = language

    def student_count(self, semester: int, potential: bool = False) -> int:
        if semester in self.items:
            return self.items[semester].student_count(semester, potential)
        return 0


@dataclass
class _Elective(BaseNode):
    def __init__(self, elective: Elective):
        kinds = elective.kinds.all()
        kind_languages = set(kinds.values_list('language', flat=True))
        languages = {
            language: _Language(
                elective,
                kinds.filter(language=language),
                language,
            )
            for language in kind_languages
        }
        super().__init__(languages)
        self.properties = {
            'pk': elective.pk,
            'name': elective.name,
            'english_name': elective.english_name,
            'codename': elective.codename,
            'text_teachers': elective.text_teachers,
            'has_russian_kind': elective.has_russian_kind,
            'has_english_kind': elective.has_english_kind,
            'has_not_fall': elective.has_not_fall,
            'has_spring': elective.has_spring,
        }

    def generate_view(self, student_id: int):
        view = (
            self.properties,
            [
                inner_item.generate_view(student_id)
                for inner_item in self.items.values()
            ],
            self.student_count(1),
            self.student_count(2),
            self.student_count(1, True),
            self.student_count(2, True),
        )
        return view


@dataclass
class _Thematic(BaseNode):
    def __init__(self, thematic: ElectiveThematic):
        electives = {
            elective.pk: _Elective(elective)
            for elective in Elective.objects.filter(
                thematic=thematic,
            ).order_by('codename')
        }
        super().__init__(electives)
        self.properties = {
            'pk': thematic.pk,
            'name': thematic.name,
            'english_name': thematic.english_name,
            'short_name': thematic.short_name,
        }

    def generate_view(self, student_id: int):
        # TODO: Этот запрос можно вынести, чтобы производить один раз?
        config, _ = ConfigModel.objects.get_or_create()
        electives_list = [
            inner_item.generate_view(student_id)
            for inner_item in self.items.values()
            if not config.block_fall or (
                    config.block_fall and inner_item.properties['has_spring']
            )
        ]
        electives_list.sort(key=lambda elective: elective[0]['codename'])
        view = (
            self.properties,
            electives_list,
        )
        return view


@dataclass
class _Data(BaseNode):
    def __init__(self):
        thematics = {
            thematic.pk: _Thematic(thematic)
            for thematic in ElectiveThematic.objects.order_by('name').all()
        }
        super().__init__(thematics)

    def generate_view(self, student_id: int):
        # TODO: Убрать этот запрос к DB тоже?
        if Student.objects.filter(person_id=student_id).exists():
            mandatory_thematics = ElectiveThematic.objects.filter(
                mandatory_thematics__student_group__students__person_id=student_id,
            ).values_list('pk', flat=True)
        else:
            mandatory_thematics = []

        return [
            inner_item.generate_view(student_id)
            for item, inner_item in self.items.items()
            if item not in mandatory_thematics
        ]

    def generate_view_thematic(self, student_id: int, thematic: ElectiveThematic):
        return self.items[thematic].generate_view(student_id)


@dataclass
class Statistic(object):
    obj = None
    data = None
    last_modified = None

    @classmethod
    def __new__(cls, *args):
        if cls.obj is None:
            cls.last_modified = dt.datetime.now()
            cls.obj = object.__new__(cls)
            logger.info('Start statistic calculating')
            cls.data = _Data()
            logger.info('Finish statistic calculating')
        return cls.obj

    def restart(self):
        logger.info('ReStart statistic calculating')
        self.last_modified = dt.datetime.now()
        self.data = _Data()
        logger.info('Finish statistic calculating')

    def add_student(
        self,
        elective: Elective,
        kind: ElectiveKind,
        student_id: int,
        potential: bool,
    ):
        self.last_modified = dt.datetime.now()
        self.data[elective.thematic.pk][elective.pk][kind.language][kind.semester][kind][potential].add_student(student_id)

    def remove_student(
        self,
        elective: Elective,
        kind: ElectiveKind,
        student_id: int,
        potential: bool,
    ):
        self.last_modified = dt.datetime.now()
        try:
            self.data[elective.thematic.pk][elective.pk][kind.language][kind.semester][kind][potential].remove_student(student_id)
        except KeyError:
            self.restart()

    def remove_student_all(
        self,
        elective: Elective,
        kind: ElectiveKind,
        student_id: int,
    ):
        self.last_modified = dt.datetime.now()
        try:
            self.data[elective.thematic.pk][elective.pk][kind.language][kind.semester][kind].remove_student_all(
                student_id
            )
        except KeyError:
            self.restart()

    def generate_view(
        self,
        student_id: int,
        thematic: Optional[ElectiveThematic] = None,
    ):
        if thematic is None:
            return self.data.generate_view(student_id)
        else:
            return self.data.generate_view_thematic(student_id, thematic)
