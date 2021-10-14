"""Model for parsing HTML page with the list of courses"""
import math

from bs4 import BeautifulSoup
import requests
import re


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

    def generate_student_groups(self):
        self.load_page()
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


if __name__ == '__main__':
    parser = Parser('https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021.html')
    print(parser.generate_student_groups())
