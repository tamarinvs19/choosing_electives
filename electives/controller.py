from collections import namedtuple, Counter
from typing import Tuple, List, Dict, Optional

from loguru import logger

from electives.models import KindOfElective, Elective, StudentOnElective, ElectiveKind, ElectiveThematic
from users.models import Person


KindWithSelectStatus = namedtuple('KindWithSelectStatus', ['kind', 'selected'])
KindWithSelectStatusAndStatistic = namedtuple('KindWithSelectStatusAndStatistic',
                                              ['kind', 'selected', 'statistic'])
ElectiveWithKinds = namedtuple('ElectiveWithKinds', ['elective', 'kinds'])


def get_electives_by_thematics(student: Person) -> Dict[ElectiveThematic, List[ElectiveWithKinds]]:
    electives = Elective.objects.all().select_related('thematic')
    groups = {thematic: [] for thematic in ElectiveThematic.objects.all()}
    for elective in electives:
        kinds = get_student_elective_kinds(student, elective)
        statistics = get_statistics(elective)
        new_kinds = [
            KindWithSelectStatusAndStatistic(
                kind.kind,
                kind.selected,
                0 if kind.kind not in statistics.keys()
                else statistics[kind.kind],
            )
            for kind in kinds
        ]
        groups[elective.thematic].append(ElectiveWithKinds(elective, new_kinds))
    return groups


def get_statistics(elective: Elective) -> Dict[ElectiveKind, int]:
    students_on_elective = StudentOnElective.objects\
        .filter(elective=elective)\
        .select_related('kind')
    kinds = Counter([soe.kind for soe in students_on_elective])
    return dict(kinds)


def get_student_elective_kinds(student: Person, elective: Elective) -> List[KindWithSelectStatus]:
    kinds_of_elective = KindOfElective.objects.filter(elective=elective).all().select_related('kind')
    kinds = [
        kind_of_elective.kind
        for kind_of_elective in kinds_of_elective
    ]

    student_on_electives = StudentOnElective.objects\
        .filter(student=student, elective=elective)\
        .all().select_related('kind')
    student_kinds = [
        student_on_elective.kind
        for student_on_elective in student_on_electives
    ]

    return [
        KindWithSelectStatus(kind, kind in student_kinds)
        for kind in kinds
    ]


def save_kinds(student: Person, elective: Elective, kind_short_names: List[str]):
    selected_kinds = [kind for kind in ElectiveKind.objects.all() if kind.short_name in kind_short_names]
    student_on_electives = StudentOnElective.objects.filter(student=student, elective=elective).all()
    student_kinds = [
        student_on_elective.kind
        for student_on_elective in student_on_electives.all()
    ]

    kinds_of_elective = KindOfElective.objects.filter(elective=elective).all()
    kinds = [
        kind_of_elective.kind
        for kind_of_elective in kinds_of_elective.all()
    ]

    for kind in selected_kinds:
        if kind in kinds:
            if kind not in student_kinds:
                StudentOnElective.objects.create(
                    student=student,
                    elective=elective,
                    kind=kind,
                )
    for kind in student_kinds:
        if kind not in selected_kinds:
            student_on_elective = StudentOnElective.objects.get(
                elective=elective,
                student=student,
                kind=kind,
            )
            student_on_elective.delete()


def change_kinds(student: Person, elective_id: int, kind_id: int) -> None:
    kind = ElectiveKind.objects.filter(id=kind_id).all()
    elective = Elective.objects.filter(id=elective_id).all()
    if len(kind) == 1 and len(elective) == 1:
        kind = kind[0]
        elective = elective[0]

        student_on_elective = StudentOnElective.objects.filter(
            student=student,
            elective=elective,
            kind=kind,
        ).all()
        if len(student_on_elective) == 1:
            student_on_elective[0].delete()
        else:
            StudentOnElective.objects.create(
                student=student,
                elective=elective,
                kind=kind,
            )


def change_exam(student: Person, elective_id: int, kind_id: int) -> Optional[bool]:
    kind = ElectiveKind.objects.filter(id=kind_id).all()
    elective = Elective.objects.filter(id=elective_id).all()
    if len(kind) == 1 and len(elective) == 1:
        kind = kind[0]
        elective = elective[0]
        if kind.credit_units == 2:
            return None

        try:
            student_on_elective = StudentOnElective.objects.get(
                student=student,
                elective=elective,
                kind=kind,
            )
        except Elective.DoesNotExist as _:
            return None

        student_on_elective.with_examination = not student_on_elective.with_examination
        student_on_elective.save()
        return student_on_elective.with_examination
