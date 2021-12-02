"""Model for parsing HTML page with the list of courses"""
import itertools
import math

from bs4 import BeautifulSoup
import requests
import re

from loguru import logger

from django.core.exceptions import ValidationError

from electives.models import ElectiveThematic, Elective, ElectiveKind, KindOfElective

RUSSIAN_URL = 'https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021.html'
ENGLISH_URL = 'https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021_en.html'
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
        lim_table = soup.find(string=re.compile('Число з.е.')).parent.parent.parent
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
        pattern1 = r'^от (\d+) до (\d+)$'
        pattern2 = r'^(\d+)$'
        pattern3 = r'^без ограничений$'
        pattern4 = r'^не более (\d+)$'

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


def main():
    parser = Parser(RUSSIAN_URL)
    parser.load_page()
    electives = parser.parse_electives()

    english_parser = Parser(ENGLISH_URL)
    english_parser.load_page()
    english_electives = english_parser.parse_electives()

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
                    english_name=english_elective['name'],
                    codename=thematic_elective['codename'],
                    thematic=thematic,
                    text_teachers=thematic_elective['teachers'],
                    description=description,
                    english_description=english_description,
                )
            for elective_type, semester in itertools.product(
                    thematic_elective['credit_type'], thematic_elective['semesters']):
                try:
                    kind = ElectiveKind.objects.create(
                        credit_units=elective_type[0],
                        language=elective_type[1],
                        semester=semester,
                    )
                except ValidationError:
                    kind = ElectiveKind.objects.get(
                        credit_units=elective_type[0],
                        language=elective_type[1],
                        semester=semester,
                    )
                if not KindOfElective.objects.filter(elective=elective, kind=kind).exists():
                    KindOfElective.objects.create(
                        elective=elective,
                        kind=kind,
                    )


if __name__ == '__main__':
    main()
