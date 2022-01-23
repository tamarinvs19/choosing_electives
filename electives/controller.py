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

    @param student: the student for whom we are generating the main page.
    @return: Dict-tree-like structure for generating main page.
    """

    statistic = Statistic()
    return statistic.generate_view(student.id)


def get_statistics(elective: Elective, kind: ElectiveKind) -> Dict[bool, int]:
    """
    Calculate the current number of applications to elective and kind.

    @param elective: elective whose statistic we should return
    @param kind: kind whose statistic we should return
    @return: Dict[bool, int]
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

    @param student: student whose applications we should change
    @param elective: elective in applications
    @return: List[KindWithSelectStatus] - list of namedtuples
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


def change_kinds(student: Person, elective: Elective, kind: ElectiveKind) -> Optional[StudentOnElective]:
    """
    If this student has applications for this elective and this kind
    we delete all of them.

    Else we create a new application for this elective and this kind
    with attached = False AND
    if this student has applications
    which differ only in language we change it to kind.language.

    @param student: person whose application we should change
    @param elective: elective where we should change kinds
    @param kind: new kind for elective
    @return: return new application or None in the first condition
    """

    similar_application = StudentOnElective.objects.filter(
        student=student,
        elective=elective,
        kind=kind,
    ).all()

    if len(similar_application) >= 1:
        similar_application.delete()
    else:
        if kind not in elective.kinds:
            return None

        max_priority = StudentOnElective.objects.filter(
            student=student,
            kind__semester=kind.semester,
            attached=False,
        ).aggregate(Max('priority'))['priority__max']

        new_priority = 0 if max_priority is None else max_priority + 1

        similar_application = StudentOnElective.objects.filter(
            student=student,
            elective=elective,
            kind__semester=kind.semester,
            kind__credit_units=kind.credit_units,
        )
        for application in similar_application:
            if application.kind.language != kind.language:
                application.kind = kind
                application.save()

        new_application = StudentOnElective.objects.create(
            student=student,
            elective=elective,
            kind=kind,
            priority=new_priority
        )
        return new_application


def change_exam(application: StudentOnElective) -> StudentOnElective:
    """
    Invert value with_examination if it is not a seminar.

    @param application: the application
    @return: updated application
    """
    if not application.is_seminar:
        application.with_examination = not application.with_examination
        application.save()
    return application


def change_kind(application: StudentOnElective, kind: ElectiveKind) -> Optional[StudentOnElective]:
    """
    Change kind for all applications where student, elective, semester and credit_units
    are match the corresponding ones in application.

    So if application is similar to the current application but has a different language
    we change this language.

    @param application: application for changing kind
    @param kind: new kind
    @return: modified application or None if this kind is not correct
    """

    if kind not in application.elective.kinds:
        return None

    similar_applications = StudentOnElective.objects.filter(
        student=application.student,
        elective=application.elective,
        kind__semester=kind.semester,
        kind__credit_units=kind.credit_units,
    )
    for application in similar_applications:
        if application.kind.language != kind.language:
            application.kind = kind
            application.save()

    StudentOnElective.objects.filter(
        student=application.student,
        attached=application.attached,
        kind__semester=application.kind.semester,
        priority__gt=application.priority,
    ).update(priority=F('priority') - 1)

    StudentOnElective.objects.filter(
        student=application.student,
        attached=application.attached,
        kind__semester=kind.semester,
        priority__gt=application.priority,
    ).update(priority=F('priority') + 1)

    application.kind = kind

    if kind.is_seminar:
        application.with_examination = False
    application.save()

    return application


def attach_application(application: StudentOnElective, target: str, new_index: int) -> Optional[StudentOnElective]:
    """
    Move application to target column with new_index.

    @param application: moving application
    @param target: name of the target column
        maybeFall / maybeSpring / fall / spring
    @param new_index: new index in the target column
    @return: modified application or None if the new kind is not correct
    """

    kind = application.kind
    elective = application.elective
    possible_kinds = elective.kinds

    semester = kind.semester
    attached = application.attached
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
        student=application.student,
        attached=application.attached,
        kind__semester=application.kind.semester,
        priority__gt=application.priority,
    ).update(priority=F('priority') - 1)

    StudentOnElective.objects.filter(
        student=application.student,
        attached=attached,
        kind__semester=new_kind.semester,
        priority__gte=new_index,
    ).update(priority=F('priority') + 1)

    application.priority = new_index
    application.kind = new_kind
    application.attached = attached
    application.save()

    return application


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
