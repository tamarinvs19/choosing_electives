"""Model for parsing HTML page with the list of courses"""

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
            print(line)
        return table

    def generate_student_groups(self):
        self.load_page()
        table = self.parse_limitations()
        print(table)


if __name__ == '__main__':
    parser = Parser('https://users.math-cs.spbu.ru/~okhotin/course_process/course_announcement_autumn2021.html')
    parser.generate_student_groups()
