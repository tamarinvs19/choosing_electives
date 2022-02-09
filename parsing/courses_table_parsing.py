"""Model for parsing HTML page with the list of courses"""
import itertools
import math

from bs4 import BeautifulSoup
import requests
import re

from loguru import logger

from electives.models import ElectiveThematic, Elective, ElectiveKind, KindOfElective, \
    CreditUnitsKind, ExamPossibility, MandatoryThematicInStudentGroup
from groups.models import StudentGroup, Curriculum, YearOfEducation

from constance import config as cfg


NO_ENGLISH_MARKER = '(no English name)'


class Parser(object):
    def __init__(self, url: str) -> None:
        self._url: str = url
        self._content = None

    def load_page(self) -> None:
        """
        Load page from self._address.
        If response status does not equal 200, raise HTTPError.
        """

        response = requests.get(self._url)
        response.raise_for_status()

        self._content = response.content

    def parse_limitations(self) -> list[dict[str, str]]:
        soup = BeautifulSoup(self._content, 'lxml')
        lim_table = soup.find(string=re.compile('# of credit units')).parent.parent.parent
        columns = ['student_group', '', 'credits', 'exams', 'light_credits', 'cs_courses']
        table = []
        for tr in lim_table.find_all('tr')[1:]:
            line = {}
            for td, column in zip(tr.find_all('td'), columns):
                line[column] = td.text
            table.append(line)
        return table

    def generate_student_groups(self) -> list[dict[str, ]]:
        table = self.parse_limitations()
        parsed_table = []
        for line in table:
            parsed_table.append({
                'name': self._parse_student_group(line['student_group']),
                'credits': self._parse_interval(line['credits']),
                'exams': self._parse_interval(line['exams']),
                'light_credits': self._parse_interval(line['light_credits']),
                'cs_courses': self._parse_interval(line['cs_courses']),
            })
        return parsed_table

    @staticmethod
    def _parse_student_group(str_student_group: str) -> tuple[str, int, str]:
        pattern = r'^(.+), \w+ (\d+) \((\w+\d+)\)$'
        match = re.search(pattern, str_student_group)
        if match is not None:
            return match[1], int(match[2]), match[3]
        raise ValueError('{0} is not a student group string form'.format(str_student_group))

    @staticmethod
    def _parse_interval(str_interval: str) -> tuple[int, int] | tuple[int, float]:
        pattern1 = r'^from (\d+) to (\d+)$'
        pattern2 = r'^(\d+)$'
        pattern3 = r'^no restrictions$'
        pattern4 = r'^at most (\d+)$'

        match1 = re.search(pattern1, str_interval)
        match2 = re.search(pattern2, str_interval)
        match3 = re.search(pattern3, str_interval)
        match4 = re.search(pattern4, str_interval)
        if match1 is not None:
            return int(match1[1]), int(match1[2])
        if match2 is not None:
            return int(match2[1]), int(match2[1])
        if match3 is not None:
            return 0, math.inf
        if match4 is not None:
            return 0, int(match4[1])
        raise ValueError('{0} is not a interval form'.format(str_interval))

    def parse_electives(self):
        soup = BeautifulSoup(self._content, 'lxml')
        titles = soup.findAll('h2')
        thematics = [title.a.text for title in titles]
        tables = [title.find_next_sibling('table') for title in titles]
        tables = list(map(self.parse_one_thematic_table, tables))
        thematic_tables = dict(zip(thematics, tables))
        return thematic_tables

    @staticmethod
    def parse_one_thematic_table(table):
        def _parse_semesters(text):
            pattern1 = r'(\d+)[^,](\d+)'
            pattern2 = r'(\d+),(\d+)'
            pattern3 = r'\w+(\d+)'

            has_odd_semester = False
            has_even_semester = False

            match1 = re.findall(pattern1, text)
            match2 = re.findall(pattern2, text)
            match3 = re.findall(pattern3, text)

            if match1:
                has_odd_semester = True
                has_even_semester = True
            if match2:
                for match in match2:
                    if any(int(sem) % 2 == 1 for sem in match):
                        has_odd_semester = True
                    if any(int(sem) % 2 == 2 for sem in match):
                        has_even_semester = True
            if match3:
                for match in match3:
                    has_odd_semester |= int(match) % 2 == 1
                    has_even_semester |= int(match) % 2 == 0
            semesters = []
            if has_odd_semester: semesters.append(1)
            if has_even_semester: semesters.append(2)
            return semesters

        def _parse_credits(texts):
            pattern_big = r'^большой курс (\S+)$'
            pattern_small = r'^малый курс (\S+)$'
            pattern_seminar = r'^семинар (\S+)$'
            languages = {
                'по-русски': 'ru',
                'по-английски': 'en',
            }

            credit_types = []
            for text in texts:
                match_big = re.search(pattern_big, text)
                match_small = re.search(pattern_small, text)
                match_seminar = re.search(pattern_seminar, text)

                if match_big is not None:
                    credit_types.append((4, languages[match_big[1]]))
                elif match_small is not None:
                    credit_types.append((3, languages[match_small[1]]))
                elif match_seminar is not None:
                    credit_types.append((2, languages[match_seminar[1]]))
            return credit_types

        columns = ['codename', 'fullname', 'credit_type', 'teachers', 'description', 'semesters']
        thematic_table = []
        for tr in table.find_all('tr'):
            line = {}
            for td, column in zip(tr.find_all('td'), columns):
                if column == 'credit_type':
                    line[column] = _parse_credits([span['title'] for span in td.findAll('span')])
                elif column == 'description':
                    line[column] = [link['href'] for link in td.findAll('a')]
                elif column == 'semesters':
                    line[column] = _parse_semesters(td.text)
                else:
                    line[column] = td.text
            thematic_table.append(line)
        return thematic_table


def create_default_kinds():
    CreditUnitsKind.objects.get_or_create(
        credit_units=2,
        russian_name='Семинар',
        english_name='Seminar',
        short_name='s',
        default_exam_possibility=ExamPossibility.ONLY_WITHOUT_EXAM
    )
    CreditUnitsKind.objects.get_or_create(
        credit_units=3,
        russian_name='Малый',
        english_name='Small',
        short_name='1',
        default_exam_possibility=ExamPossibility.DEFAULT
    )
    CreditUnitsKind.objects.get_or_create(
        credit_units=4,
        russian_name='Большой',
        english_name='Large',
        short_name='2',
        default_exam_possibility=ExamPossibility.DEFAULT
    )


def create_default_mandatory_thematics():
    sp_mandatory_thematics = ElectiveThematic.objects.filter(name__contains='обязательные курсы СП')
    sps = StudentGroup.objects.filter(curriculum__name__contains='Modern Programming')
    for thematic, sp in itertools.product(sp_mandatory_thematics, sps):
        MandatoryThematicInStudentGroup.objects.get_or_create(
            thematic=thematic,
            student_group=sp,
        )


def main_electives():
    parser = Parser(cfg.RUSSIAN_URL)
    parser.load_page()
    electives = parser.parse_electives()

    english_parser = Parser(cfg.ENGLISH_URL)
    english_parser.load_page()
    english_electives = english_parser.parse_electives()

    elective_ids = []

    for (thematic_name, thematic_electives), (english_name, thematic_english_electives) in zip(
            electives.items(), english_electives.items()):
        if ElectiveThematic.objects.filter(name=thematic_name).exists():
            thematic = ElectiveThematic.objects.get(name=thematic_name)
            thematic.english_name = english_name
            thematic.save()
        else:
            thematic = ElectiveThematic.objects.create(name=thematic_name, english_name=english_name)
        for thematic_elective, english_elective in zip(thematic_electives, thematic_english_electives):

            description, english_description = '', ''
            if NO_ENGLISH_MARKER in english_elective['fullname']:
                description = thematic_elective['description'][0]
            elif len(thematic_elective['description']) == 1:
                english_description = thematic_elective['description'][0]
            else:
                description = thematic_elective['description'][0]
                english_description = thematic_elective['description'][1]

            if Elective.objects.filter(codename=thematic_elective['codename']).exists():
                elective = Elective.objects.get(codename=thematic_elective['codename'])
                elective.name = thematic_elective['fullname']
                if NO_ENGLISH_MARKER not in english_elective['fullname']:
                    elective.english_name = english_elective['fullname']
                elective.thematic = thematic
                elective.text_teachers = thematic_elective['teachers']
                elective.description = description
                elective.english_description = english_description
                elective.save()
            else:
                elective = Elective.objects.create(
                    name=thematic_elective['fullname'],
                    english_name=english_elective['fullname'],
                    codename=thematic_elective['codename'],
                    thematic=thematic,
                    text_teachers=thematic_elective['teachers'],
                    description=description,
                    english_description=english_description,
                )

            elective_ids.append(elective.id)

            for elective_type, semester in itertools.product(
                    thematic_elective['credit_type'], thematic_elective['semesters']):
                # Now whe get the first of kinds with credit_units
                # Next time it will be read in the parsing table
                credit_units_kind = CreditUnitsKind.objects.filter(
                    credit_units=elective_type[0],
                ).all()[0]

                kind, _ = ElectiveKind.objects.get_or_create(
                    credit_units_kind=credit_units_kind,
                    language=elective_type[1],
                    semester=semester,
                )
                kind_of_elective, _ = KindOfElective.objects.get_or_create(
                    elective=elective,
                    kind=kind,
                )
                kind_of_elective.exam_possibility = kind.credit_units_kind.default_exam_possibility

    Elective.objects.exclude(id__in=elective_ids).delete()


def main_programs():
    parser = Parser(cfg.ENGLISH_URL)
    parser.load_page()
    student_groups = parser.generate_student_groups()
    codenames = []
    groups_dict = {}
    for group_data in student_groups:
        codenames.append(group_data['name'][2])
        groups_dict[group_data['name'][2]] = group_data
    codenames = zip(codenames[::2], codenames[1::2])

    group_ids = []
    for fall_code, spring_code in codenames:
        fall_data = groups_dict[fall_code]
        spring_data = groups_dict[spring_code]
        year = fall_data['name'][1] // 2 + 1

        if year != spring_data['name'][1] // 2:
            raise ValueError('Incorrect pair: {0} and {1}'.format(fall_code, spring_code))

        curriculum, _ = Curriculum.objects.get_or_create(name=fall_data['name'][0])
        year_of_education, _ = YearOfEducation.objects.get_or_create(year=year)
        student_group, _ = StudentGroup.objects.get_or_create(curriculum=curriculum, course_value=year_of_education)

        group_ids.append(student_group.id)

        student_group.min_credit_unit_fall = fall_data['credits'][0]
        student_group.max_credit_unit_fall = fall_data['credits'][1]
        student_group.min_credit_unit_spring = spring_data['credits'][0]
        student_group.max_credit_unit_spring = spring_data['credits'][1]

        if fall_data['exams'][0] != math.inf:
            student_group.min_number_of_exams_fall = fall_data['exams'][0]
        else:
            student_group.min_number_of_exams_fall = None
        if fall_data['exams'][1] != math.inf:
            student_group.max_number_of_exams_fall = fall_data['exams'][1]
        else:
            student_group.max_number_of_exams_fall = None

        if spring_data['exams'][0] != math.inf:
            student_group.min_number_of_exams_spring = spring_data['exams'][0]
        else:
            student_group.min_number_of_exams_spring = None
        if spring_data['exams'][1] != math.inf:
            student_group.max_number_of_exams_spring = spring_data['exams'][1]
        else:
            student_group.max_number_of_exams_spring = None

        if fall_data['light_credits'][1] != math.inf:
            student_group.light_credit_unit_fall = fall_data['light_credits'][1]
        else:
            student_group.light_credit_unit_fall = None
        if spring_data['light_credits'][1] != math.inf:
            student_group.light_credit_unit_spring = spring_data['light_credits'][1]
        else:
            student_group.light_credit_unit_spring = None

        if fall_data['cs_courses'][1] != math.inf:
            student_group.max_cs_courses_fall = fall_data['cs_courses'][1]
        else:
            student_group.max_cs_courses_fall = None
        if spring_data['cs_courses'][1] != math.inf:
            student_group.max_cs_courses_spring = spring_data['cs_courses'][1]
        else:
            student_group.max_cs_courses_spring = None

        student_group.save()

    StudentGroup.objects.exclude(id__in=group_ids).delete()


if __name__ == '__main__':
    create_default_kinds()
    main_programs()
    main_electives()
    create_default_mandatory_thematics()
