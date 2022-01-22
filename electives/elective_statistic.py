from collections import Counter
from dataclasses import dataclass
from typing import Optional

from django.db.models import QuerySet

from loguru import logger

from electives.models import ElectiveThematic, Elective, ElectiveKind
from groups.models import Student


@dataclass
class BaseNode:
    def __init__(self, items, *args, **kwargs):
        self.items = items

    def __getitem__(self, item):
        return self.items[item]

    def generate_view(self, student_id: int):
        return {item: inner_item.generate_view(student_id) for item, inner_item in self.items.items()}

    def student_count(self, semester: int) -> int:
        return sum(inner_item.student_count(semester) for inner_item in self.items.values())


@dataclass
class _MaybeCounter(BaseNode):
    def __init__(self, elective: Elective, kind: ElectiveKind, attached: bool):
        items = Counter(
            sone.student.id
            for sone in elective.studentonelective_set.filter(kind=kind, attached=attached)
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

    def student_count(self, _: int) -> int:
        return len(self.items[True].items.keys())

    def remove_student_all(self, student_id: int) -> None:
        for maybe_counter in self.items.values():
            maybe_counter.remove_student_all(student_id)


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

    def student_count(self, semester: int) -> int:
        if semester in self.items:
            return self.items[semester].student_count(semester)
        return 0


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

    def generate_view(self, student_id: int):
        view_dict = {
            item: (
                inner_item.generate_view(student_id),
                inner_item.student_count(1),
                inner_item.student_count(2),
            )
            for item, inner_item in self.items.items()
        }
        return view_dict


@dataclass
class _Data(BaseNode):
    def __init__(self):
        thematics = {
            thematic: _Thematic(thematic)
            for thematic in ElectiveThematic.objects.all()
        }
        super().__init__(thematics)

    def generate_view(self, student_id: int):
        if Student.objects.filter(person_id=student_id).exists():
            mandatory_thematics = ElectiveThematic.objects.filter(
                mandatory_thematics__student_group__students__person_id=student_id,
            ).all()
        else:
            mandatory_thematics = []

        return {
            item: inner_item.generate_view(student_id)
            for item, inner_item in self.items.items()
            if item not in mandatory_thematics
        }

    def generate_view_thematic(self, student_id: int, thematic: ElectiveThematic):
        return self.items[thematic].generate_view(student_id)


@dataclass
class Statistic(object):
    obj = None
    data = None

    @classmethod
    def __new__(cls, *args):
        if cls.obj is None:
            cls.obj = object.__new__(cls)
            logger.info('Start statistic calculating')
            cls.data = _Data()
            logger.info('Finish statistic calculating')
        return cls.obj

    def add_student(self, elective: Elective, kind: ElectiveKind, student_id: int, attached: bool):
        self.data[elective.thematic][elective][kind.language][kind.semester][kind][attached].add_student(student_id)

    def remove_student(self, elective: Elective, kind: ElectiveKind, student_id: int, attached: bool):
        self.data[elective.thematic][elective][kind.language][kind.semester][kind][attached].remove_student(student_id)

    def generate_view(self, student_id: int, thematic: Optional[ElectiveThematic] = None):
        if thematic is None:
            return self.data.generate_view(student_id)
        else:
            return self.data.generate_view_thematic(student_id, thematic)

    def remove_student_all(self, elective: Elective, kind: ElectiveKind, student_id: int):
        self.data[elective.thematic][elective][kind.language][kind.semester][kind].remove_student_all(student_id)
