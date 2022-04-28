from collections import namedtuple, defaultdict
from typing import List, Dict, Optional

import xlsxwriter

from django.db.models import F, Max, Count, QuerySet
from loguru import logger
from model_utils import FieldTracker

from apps.electives.elective_statistic import Statistic
from apps.electives.models import KindOfElective, Elective, StudentOnElective, ElectiveKind
from apps.parsing.models import ConfigModel
from apps.users.models import Person


KindWithSelectStatus = namedtuple('KindWithSelectStatus', ['kind', 'selected'])


def get_electives_by_thematics(student: Person) -> object:
    """
    Generate information for creating the main page with the current student.

    @param student: the student for whom we are generating the main page.
    @return: Dict-tree-like structure for generating main page.
    """

    statistic = Statistic()
    return statistic.generate_view(student.pk)


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
    students: dict[bool, set[Person]] = {True: set(), False: set()}
    for application in students_on_elective:
        attached = application.attached
        if application.student not in students[attached]:
            students[attached].add(application.student)
            counts[attached] += 1
    return counts


def get_student_elective_kinds(
    student: Person,
    elective: Elective,
) -> List[KindWithSelectStatus]:
    """
    Generate a list of structures KindWithSelectStatus
    for the current student and elective.

    @param student: student whose applications we should change
    @param elective: elective in applications
    @return: List[KindWithSelectStatus] - list of namedtuples
    """

    kinds_of_elective = KindOfElective.objects.filter(
        elective=elective
    ).all().select_related('kind')

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


def update_similar_application(
    kind: ElectiveKind,
    similar_applications: list[StudentOnElective],
    kind_of_elective: KindOfElective,
) -> None:
    """
    Update applications from similar_applications
    """

    for similar_application in similar_applications:
        if similar_application.kind.language != kind.language:
            if similar_application.with_examination and kind_of_elective.only_without_exam:
                similar_application.with_examination = False
            if not similar_application.with_examination and kind_of_elective.only_with_exam:
                similar_application.with_examination = True
            similar_application.kind = kind
            similar_application.save()


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

    kind_similar_application = StudentOnElective.objects.filter(
        student=student,
        elective=elective,
        kind=kind,
    ).all()

    if len(kind_similar_application) >= 1:
        success = remove_applications(kind_similar_application)
        if not success:
            return None
    else:
        if kind not in elective.kinds.all():
            return None
        if not check_application_operation(kind):
            return None

        max_priority = StudentOnElective.objects.filter(
            student=student,
            kind__semester=kind.semester,
            attached=False,
        ).aggregate(Max('priority'))['priority__max']

        new_priority = 0 if max_priority is None else max_priority + 1

        similar_applications = StudentOnElective.objects.filter(
            student=student,
            elective=elective,
            kind__semester=kind.semester,
            kind__credit_units_kind__credit_units=kind.credit_units,
        )
        kind_of_elective = KindOfElective.objects.get(
            elective=elective,
            kind=kind,
        )
        update_similar_application(kind, similar_applications, kind_of_elective)

        new_application = StudentOnElective.objects.create(
            student=student,
            elective=elective,
            kind=kind,
            priority=new_priority,
            with_examination=kind_of_elective.exam_is_possible,
        )
        return new_application


def change_exam(application: StudentOnElective) -> Optional[StudentOnElective]:
    """
    Invert value with_examination if it is possible.

    @param application: the application
    @return: updated application or None if updating is impossible
    """
    kind_of_elective = application.kind_of_elective
    if not check_application_operation(application.kind, application.tracker):
        return None
    if kind_of_elective.changing_exam_is_possible:
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

    if kind not in application.elective.kinds.all():
        return None
    if not check_application_operation(kind):
        return None
    if not check_application_operation(application.kind, application.tracker):
        return None

    similar_applications = StudentOnElective.objects.filter(
        student=application.student,
        elective=application.elective,
        kind__semester=kind.semester,
        kind__credit_units_kind__credit_units=kind.credit_units,
    ).exclude(
        id=application.id,
    )

    kind_of_elective = KindOfElective.objects.get(
        elective=application.elective,
        kind=kind,
    )

    update_similar_application(kind, similar_applications, kind_of_elective)

    if application.kind.semester != kind.semester:
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

    if kind_of_elective.only_without_exam:
        application.with_examination = False
    elif kind_of_elective.only_with_exam:
        application.with_examination = True

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

    if not check_application_operation(application.kind, application.tracker):
        return None

    kind = application.kind
    elective = application.elective
    possible_kinds = elective.kinds

    semester = kind.semester
    attached = application.attached
    if target == 'maybeFall':
        attached = False
        semester = 1
    elif target == 'maybeSpring':
        attached = False
        semester = 2
    elif target == 'fall':
        attached = True
        semester = 1
    elif target == 'spring':
        attached = True
        semester = 2
    try:
        new_kind = possible_kinds.get(
            credit_units_kind__credit_units=kind.credit_units,
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

    kind_of_elective = KindOfElective.objects.get(
        elective=elective,
        kind=new_kind,
    )
    application.priority = new_index
    application.kind = new_kind
    application.attached = attached
    application.with_examination = kind_of_elective.exam_is_possible and application.with_examination
    application.save()

    return application


def check_application_operation(
    application_kind: ElectiveKind,
    tracker: Optional[FieldTracker] = None,
) -> bool:
    """
    Checks whether it is possible to delete, create or update application with application_kind and tracker.

    @param application_kind: current or new kind
    @param tracker: [Optional] tracker if exists

    @return True if kind was not blocked and False else
    """
    config, _ = ConfigModel.objects.get_or_create()
    if config.block_fall_applications:
        if application_kind.semester == 1:
            return False
        if tracker is not None and 'kind' in tracker.changed():
            if tracker.changed()['kind'].semester == 1:
                return False
    elif config.block_spring_applications:
        if application_kind.semester == 2:
            return False
        if tracker is not None and 'kind' in tracker.changed():
            if tracker.changed()['kind'].semester == 2:
                return False
    return True


def remove_applications(applications: QuerySet[StudentOnElective] | StudentOnElective) -> bool:
    """
    Remove applications to target column with new_index.

    @param applications: removing applications

    @return status, True if application was removed and False else
    """
    if isinstance(applications, StudentOnElective):
        applications = [applications]
    config, _ = ConfigModel.objects.get_or_create()
    for application in applications:
        if not check_application_operation(application.kind, application.tracker):
            return False
    count, _ = applications.delete()
    return count > 0


def generate_application_row(student: Person, semester: int) -> str:
    """
    Generate an application row for this student and this semester.

    @param student: Person object
    @param semester: the number of semester, 1 is fall, 2 if spring

    @return applications code
    """
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
    """
    Calculate the count of credit units.

    @param student: Person object
    @param semester: the number of semester, 1 is fall, 2 if spring
    @param attached: which applications we need to calc

    @return count of credit units
    """
    return sum(
        application.credit_units
        for application in StudentOnElective.objects.filter(
            student=student,
            attached=attached,
            kind__semester=semester,
        )
    )


def duplicate_application(application: StudentOnElective) -> Optional[StudentOnElective]:
    """
    Create a copy of this application

    @param application: application for creating copy

    @return new application or None if creating is impossible
    """

    if not check_application_operation(application.kind):
        return None

    StudentOnElective.objects.filter(
        student=application.student,
        attached=application.attached,
        kind__semester=application.kind.semester,
        priority__gt=application.priority,
    ).update(priority=F('priority') + 1)

    new_student_on_elective = StudentOnElective.objects.create(
        student=application.student,
        elective=application.elective,
        kind=application.kind,
        with_examination=application.with_examination,
        attached=application.attached,
        priority=application.priority + 1
    )
    return new_student_on_elective


def generate_summary_table() -> str:
    """
    Create a summary table for downloading.

    @return file name
    """

    workbook_name = 'tables.xlsx'
    workbook = xlsxwriter.Workbook(workbook_name)
    worksheet = workbook.add_worksheet()

    kinds = sorted(
        ElectiveKind.objects.all(),
        key=lambda kind: (kind.semester, kind.credit_units, kind.language)
    )
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
