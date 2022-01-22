from collections import namedtuple, defaultdict
from typing import List, Dict, Optional

import xlsxwriter

from django.db.models import F, Max, Count

from loguru import logger

from electives.elective_statistic import Statistic
from electives.models import KindOfElective, Elective, StudentOnElective, ElectiveKind
from users.models import Person


KindWithSelectStatus = namedtuple('KindWithSelectStatus', ['kind', 'selected'])


def get_electives_by_thematics(student: Person) -> object:
    """
    Generate information for creating the main page with the current student.

    Returns:
        Dict-tree-like structure for generating main page.
    """

    statistic = Statistic()
    return statistic.generate_view(student.id)


def get_statistics(elective: Elective, kind: ElectiveKind) -> Dict[bool, int]:
    """
    Calculate the current number of applications to elective and kind.

    Returns:
        Dict[bool, int]
            Key True: the number of attached applications
            Key False: the number of no-attached applications
    """

    students_on_elective = StudentOnElective.objects.filter(
        elective=elective,
        kind=kind,
    )
    counts = {True: 0, False: 0}
    students = {True: set(), False: set()}
    for application in students_on_elective:
        attached = application.attached
        if application.student not in students[attached]:
            students[attached].add(application.student)
            counts[attached] += 1
    return counts


def get_student_elective_kinds(student: Person, elective: Elective) -> List[KindWithSelectStatus]:
    """
    Generate a list of structures KindWithSelectStatus
    for the current student and elective.

    Returns:
        List[KindWithSelectStatus] - list of namedtuples
    """

    kinds_of_elective = KindOfElective.objects.filter(elective=elective).all().select_related('kind')

    def compare(self):
        return self.language, self.semester, self.credit_units

    kinds = [
        kind_of_elective.kind
        for kind_of_elective in kinds_of_elective
    ]
    kinds.sort(key=compare)

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


def save_kinds(student: Person, elective: Elective, kind_short_names: List[str]) -> None:
    """
    Save the applications with selected kinds.
    """

    student_on_electives = StudentOnElective.objects.filter(
        student=student,
        elective=elective,
    ).select_related(
        'kind',
    ).all()
    student_kinds = [
        student_on_elective.kind
        for student_on_elective in student_on_electives
    ]

    elective_kinds = [
        kind_of_elective.kind
        for kind_of_elective in elective.kinds.all()
    ]

    selected_kinds = [
        kind for kind in ElectiveKind.objects.all()
        if kind.short_name in kind_short_names
    ]

    # Add the applications with selected kinds
    for kind in selected_kinds:
        if kind in elective_kinds and kind not in student_kinds:
            max_current_priority = StudentOnElective.objects.filter(
                student=student,
                elective=elective,
                kind__semester=kind.semester,
                attached=False,
            ).aggregate(Max('priority'))['priority__max']

            if max_current_priority is None:
                new_priority = 0
            else:
                new_priority = max_current_priority + 1

            StudentOnElective.objects.create(
                student=student,
                elective=elective,
                kind=kind,
                priority=new_priority,
            )

    # Remove the existing applications with unselected kinds
    for kind in student_kinds:
        if kind not in selected_kinds:
            StudentOnElective.objects.get(
                elective=elective,
                student=student,
                kind=kind,
            ).delete()


def change_kinds(student: Person, elective_id: int, kind_id: int) -> Optional[StudentOnElective]:
    """
    Если у студента есть заявления на этот курс, они удаляются,
    если нет, то добавляется одно в maybe
    """
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
        if len(student_on_elective) >= 1:
            student_on_elective.delete()
        else:
            new_priority = StudentOnElective.objects.filter(
                student=student,
                kind__semester=kind.semester,
                attached=False,
            ).aggregate(Max('priority'))['priority__max']

            if new_priority is None:
                new_priority = 0
            else:
                new_priority += 1

            applications = StudentOnElective.objects.filter(
                student=student,
                elective=elective,
                kind__semester=kind.semester,
                kind__credit_units=kind.credit_units,
            )
            for application in applications:
                if application.kind.language != kind.language:
                    application.kind = kind
                    application.save()

            application = StudentOnElective.objects.create(
                student=student,
                elective=elective,
                kind=kind,
                priority=new_priority
            )
            return application


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

    applications = StudentOnElective.objects.filter(
        student=student_on_elective.student,
        elective=student_on_elective.elective,
        kind__semester=kind.semester,
        kind__credit_units=kind.credit_units,
    )
    for application in applications:
        if application.kind.language != kind.language:
            application.kind = kind
            application.save()

    StudentOnElective.objects.filter(
        student=student_on_elective.student,
        attached=student_on_elective.attached,
        kind__semester=student_on_elective.kind.semester,
        priority__gt=student_on_elective.priority,
    ).update(priority=F('priority') - 1)

    StudentOnElective.objects.filter(
        student=student_on_elective.student,
        attached=student_on_elective.attached,
        kind__semester=kind.semester,
        priority__gt=student_on_elective.priority,
    ).update(priority=F('priority') + 1)

    student_on_elective.kind = kind

    if kind.is_seminar:
        student_on_elective.with_examination = False
    student_on_elective.save()

    return student_on_elective


def attach_application(student_on_elective_id: int, target: str, new_index: int) -> Optional[StudentOnElective]:
    try:
        student_on_elective = StudentOnElective.objects.get(
            id=student_on_elective_id,
        )
    except StudentOnElective.DoesNotExist as _:
        return None

    kind = student_on_elective.kind
    elective = student_on_elective.elective
    possible_kinds = elective.kinds

    semester = kind.semester
    attached = student_on_elective.attached
    match target:
        case 'maybeFall':
            attached = False
            semester = 1
        case 'maybeSpring':
            attached = False
            semester = 2
        case 'fall':
            attached = True
            semester = 1
        case 'spring':
            attached = True
            semester = 2
    try:
        new_kind = possible_kinds.get(
                credit_units=kind.credit_units,
                language=kind.language,
                semester=semester,
        )
    except ElectiveKind.DoesNotExist as _:
        return None

    StudentOnElective.objects.filter(
        student=student_on_elective.student,
        attached=student_on_elective.attached,
        kind__semester=student_on_elective.kind.semester,
        priority__gt=student_on_elective.priority,
    ).update(priority=F('priority') - 1)

    StudentOnElective.objects.filter(
        student=student_on_elective.student,
        attached=attached,
        kind__semester=new_kind.semester,
        priority__gte=new_index,
    ).update(priority=F('priority') + 1)

    student_on_elective.priority = new_index
    student_on_elective.kind = new_kind
    student_on_elective.attached = attached
    student_on_elective.save()

    return student_on_elective


def remove_application(application_id: int) -> None:
    student_on_elective = StudentOnElective.objects.get(id=application_id)
    student_on_elective.delete()


def generate_application_row(student: Person, semester: int) -> str:
    return ' '.join(
        [
            application.short_name
            for application in StudentOnElective.objects.filter(
                student=student,
                kind__semester=semester,
                attached=True,
            ).order_by('priority')
        ]
    )


def calc_sum_credit_units(student: Person, semester: int, attached: bool = True) -> int:
    return sum(
        application.credit_units
        for application in StudentOnElective.objects.filter(
            student=student,
            attached=attached,
            kind__semester=semester,
        )
    )


def duplicate_application(application_id: int) -> StudentOnElective:
    student_on_elective = StudentOnElective.objects.get(id=application_id)

    StudentOnElective.objects.filter(
        student=student_on_elective.student,
        attached=student_on_elective.attached,
        kind__semester=student_on_elective.kind.semester,
        priority__gt=student_on_elective.priority,
    ).update(priority=F('priority') + 1)

    new_student_on_elective = StudentOnElective.objects.create(
        student=student_on_elective.student,
        elective=student_on_elective.elective,
        kind=student_on_elective.kind,
        with_examination=student_on_elective.with_examination,
        attached=student_on_elective.attached,
        priority=student_on_elective.priority + 1
    )
    return new_student_on_elective


def generate_summary_table():
    workbook_name = 'tables.xlsx'
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    kinds = sorted(ElectiveKind.objects.all(), key=lambda kind: (kind.semester, kind.credit_units, kind.language))
    headers = [
        'Codename',
        'Elective russian name',
        'Elective english name',
        'Thematic',
        'Number of students'
    ] + [
        str(kind) for kind in kinds
    ]

    electives = Elective.objects.prefetch_related('studentonelective_set', 'kinds')

    data = []
    for elective in electives:
        elective_data = defaultdict(str)
        for kind in elective.kinds.all():
            filtered_data = elective.studentonelective_set.filter(
                kind=kind,
            )
            elective_data[kind.long_name] = filtered_data.filter(
                attached=True,
            ).aggregate(
                count=Count('student__id', distinct=True)
            )['count']
            elective_data[f'MAYBE {kind.long_name}'] = filtered_data.filter(
                attached=False,
            ).aggregate(
                count=Count('student__id', distinct=True)
            )['count']
        number_of_students = elective.studentonelective_set.filter(
            attached=True,
        ).aggregate(
            count=Count('student__id', distinct=True)
        )['count']
        new_row = [
                      elective.codename,
                      elective.name,
                      elective.english_name,
                      elective.thematic.english_name,
                      number_of_students,
                  ] + [
            elective_data[kind.long_name] for kind in kinds
        ]
        data.append(new_row)

    worksheet.write_row(0, 0, headers)
    for row_num, row in enumerate(data):
        worksheet.write_row(row_num + 1, 0, data[row_num])
    workbook.close()
    return workbook_name
