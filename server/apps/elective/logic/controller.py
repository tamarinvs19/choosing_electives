from collections import namedtuple, Counter
from typing import List, Dict, Optional

from loguru import logger

from .elective_statistic import Statistic
from ..models import KindOfElective, Elective, StudentOnElective, ElectiveKind, Person


KindWithSelectStatus = namedtuple('KindWithSelectStatus', ['kind', 'selected'])
KindWithSelectStatusAndStatistic = namedtuple('KindWithSelectStatusAndStatistic',
                                              ['kind', 'selected', 'statistic'])
ElectiveWithKinds = namedtuple('ElectiveWithKinds', ['elective', 'kinds'])

# statistic = Statistic()


def get_electives_by_thematics(student: Person):
    pass
    # return statistic.generate_view(student.id)


def get_statistics(elective: Elective) -> Dict[ElectiveKind, int]:
    students_on_elective = StudentOnElective.objects.filter(
        elective=elective
    ).select_related(
        'kind'
    )
    kinds = Counter([soe.kind for soe in students_on_elective])
    return dict(kinds)


def get_student_elective_kinds(student: Person, elective: Elective) -> List[KindWithSelectStatus]:
    kinds_of_elective = KindOfElective.objects.filter(elective=elective).all().select_related('kind')
    kinds = [
        kind_of_elective.kind
        for kind_of_elective in kinds_of_elective
    ]

    student_on_electives = StudentOnElective.objects.filter(
        student=student, elective=elective,
    ).select_related(
        'kind'
    ).all()
    student_kinds = {
        student_on_elective.kind
        for student_on_elective in student_on_electives
    }

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
                statistic.add_student(elective, kind, student.id)
    for kind in student_kinds:
        if kind not in selected_kinds:
            student_on_elective = StudentOnElective.objects.get(
                elective=elective,
                student=student,
                kind=kind,
            )
            student_on_elective.delete()
            statistic.remove_student(elective, kind, student.id)


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
            statistic.remove_student(elective, kind, student.id)
        else:
            StudentOnElective.objects.create(
                student=student,
                elective=elective,
                kind=kind,
            )
            statistic.add_student(elective, kind, student.id)


def change_exam(student_on_elective_id: int) -> Optional[StudentOnElective]:
    try:
        student_on_elective = StudentOnElective.objects.get(
            id=student_on_elective_id,
        )
    except StudentOnElective.DoesNotExist as _:
        return None

    student_on_elective.with_examination = not student_on_elective.with_examination
    student_on_elective.save()
    return student_on_elective


def change_kind(student_on_elective_id: int, kind_id: int) -> Optional[StudentOnElective]:
    try:
        student_on_elective = StudentOnElective.objects.get(
            id=student_on_elective_id,
        )
    except StudentOnElective.DoesNotExist as _:
        return None
    try:
        kind = ElectiveKind.objects.get(
            id=kind_id,
        )
    except ElectiveKind.DoesNotExist as _:
        return None

    student_on_elective.kind = kind
    statistic.remove_student(student_on_elective.elective, student_on_elective.kind, student_on_elective.student.id)
    statistic.add_student(student_on_elective.elective, kind, student_on_elective.student.id)
    if kind.is_seminar:
        student_on_elective.with_examination = False
    student_on_elective.save()
    return student_on_elective


def attach_application(student_on_elective_id: int) -> Optional[StudentOnElective]:
    try:
        student_on_elective = StudentOnElective.objects.get(
            id=student_on_elective_id,
        )
    except StudentOnElective.DoesNotExist as _:
        return None

    student_on_elective.attached = True
    student_on_elective.save()
    return student_on_elective


# def get_electives_by_thematics(student: Person, statistic: Statistic):
#     selected_kind = StudentOnElective.objects.filter(student=student)
#     return statistic.data
