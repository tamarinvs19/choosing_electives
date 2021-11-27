from .person_model import Person
from .elective_model import Elective, ElectiveKind, ElectiveThematic, \
    StudentOnElective, KindOfElective, MandatoryElectiveInStudentGroup
from .student_groups_model import Curriculum, YearOfEducation, StudentGroup

__all__ = [
    'Person',
    'Elective',
    'ElectiveKind',
    'ElectiveThematic',
    'StudentOnElective',
    'KindOfElective',
    'Curriculum',
    'StudentGroup',
    'YearOfEducation',
]
