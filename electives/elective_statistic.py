from collections import Counter
from dataclasses import dataclass
from django.db.models import QuerySet

from loguru import logger

from electives.models import ElectiveThematic, Elective, ElectiveKind


@dataclass
class BaseNode:
    def __init__(self, items, *args, **kwargs):
        self.items = items

    def __getitem__(self, item):
        return self.items[item]

    def generate_view(self, student_id: int):
        return {item: inner_item.generate_view(student_id) for item, inner_item in self.items.items()}


@dataclass
class _ApplicationCounter(BaseNode):
    def __init__(self, elective: Elective, kind: ElectiveKind):
        items = Counter(
            sone.student.id
            for sone in elective.studentonelective_set.filter(kind=kind)
        )
        super().__init__(items)

    def add_student(self, student_id: int):
        self.items[student_id] += 1

    def remove_student(self, student_id: int):
        if student_id in self.items:
            self.items[student_id] -= 1

    def generate_view(self, student_id: int):
        ids = self.items.keys()
        return len(ids), student_id in ids


@dataclass
class _Semester(BaseNode):
    def __init__(self, elective: Elective, kinds: QuerySet[ElectiveKind]):
        kinds = {
            kind_semester: _ApplicationCounter(elective, kind_semester)
            for kind_semester in kinds
        }
        super().__init__(kinds)


@dataclass
class _Language(BaseNode):
    def __init__(self, elective: Elective, kinds: QuerySet[ElectiveKind]):
        semesters = {
            kind_lang.semester: _Semester(elective, kinds.filter(semester=kind_lang.semester))
            for kind_lang in kinds
        }
        super().__init__(semesters)


@dataclass
class _Elective(BaseNode):
    def __init__(self, elective: Elective):
        kinds = elective.kinds.all()
        languages = {
            kind.language: _Language(elective, kinds.filter(language=kind.language))
            for kind in kinds
        }
        super().__init__(languages)


@dataclass
class _Thematic(BaseNode):
    def __init__(self, thematic: ElectiveThematic):
        electives = {
            elective: _Elective(elective)
            for elective in Elective.objects.filter(thematic=thematic)
        }
        super().__init__(electives)


@dataclass
class _Data(BaseNode):
    def __init__(self):
        thematics = {
            thematic: _Thematic(thematic)
            for thematic in ElectiveThematic.objects.all()
        }
        super().__init__(thematics)


@dataclass
class Statistic(object):
    def __init__(self):
        self.data = _Data()

    def add_student(self, elective: Elective, kind: ElectiveKind, student_id: int):
        self.data[elective.thematic][elective][kind.language][kind.semester][kind].add_student(student_id)

    def remove_student(self, elective: Elective, kind: ElectiveKind, student_id: int):
        self.data[elective.thematic][elective][kind.language][kind.semester][kind].remove_student(student_id)

    def generate_view(self, student_id: int):
        return self.data.generate_view(student_id)


def _load_data():
    data = {}
    thematics = ElectiveThematic.objects.all()
    for thematic in thematics:
        statistic_inside_thematic = {}
        electives = Elective.objects.filter(thematic=thematic)
        for elective in electives:
            kinds = elective.kinds.all()
            kind_by_lang_semester = {
                kind.language: {
                    kind_lang.semester: {
                        kind_semester: Counter(
                            sone.student.id
                            for sone in elective.studentonelective_set.filter(kind=kind_semester)
                        )
                        for kind_semester in kinds.filter(language=kind.language, semester=kind_lang.semester)
                    } for kind_lang in kinds.filter(language=kind.language)
                } for kind in kinds
            }
            statistic_inside_thematic[elective] = kind_by_lang_semester
        data[thematic] = statistic_inside_thematic
    return data
