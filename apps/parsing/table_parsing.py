import csv
import functools
from itertools import product
import re
import random
import string

from loguru import logger

from apps.electives.models import ElectiveThematic, Elective, ElectiveKind, CreditUnitsKind, KindOfElective


def generate_random_error_name():
    return 'ErrorName___' + ''.join(random.choices(string.ascii_letters, k=6))


def create_short_thematic_keys():
    thematic_keys = {
        'А': 'Aлгебра',
        'АД': 'Анализ данных',
        'ДМЛ': 'Дискретная математика и логика',
        'ГиТ': 'Геометрия и топология',
        'МФ': 'Математическая физика',
        'ДУДС': 'Дифференциальные уравнения и динамические системы',
        'И': 'Информатика',
        'МА': 'Математический анализ',
        'П': 'Программирование',
        'По': 'Программирование (обязательные курсы СП)',
        'Р': 'Разное',
        'ТВ': 'Теория вероятностей',
        'ТИ': 'Теоретическая информатика',
    }
    for key, value in thematic_keys.items():
        thematic, created = ElectiveThematic.objects.get_or_create(
            name=value,
        )
        thematic.short_name = key
        if created:
            thematic.english_name = generate_random_error_name()
        thematic.save()


def parse_credit_types(type_row: str):
    type_row = type_row.replace(' ', '')
    kind_codes = type_row.split(',')
    return kind_codes


def parse_semesters(text_semesters: str):
    text_semesters = text_semesters.replace(' ', '')

    pattern1 = r'\w+(\d+)-(\d+)'
    pattern2 = r'\w(\d+),(\d+)'
    pattern3 = r'\w+(\d+)'

    has_odd_semester = False
    has_even_semester = False

    for text in text_semesters.split(','):
        match1 = re.findall(pattern1, text)
        match2 = re.findall(pattern2, text)
        match3 = re.findall(pattern3, text)

        if match1:
            has_odd_semester = True
            has_even_semester = True
        if match2:
            for match_ in match2:
                if any(int(sem) % 2 == 1 for sem in match_):
                    has_odd_semester = True
                if any(int(sem) % 2 == 2 for sem in match_):
                    has_even_semester = True
        if match3:
            for match_ in match3:
                has_odd_semester |= int(match_) % 2 == 1
                has_even_semester |= int(match_) % 2 == 0
    semesters = []
    if has_odd_semester:
        semesters.append(1)
    if has_even_semester:
        semesters.append(2)
    return semesters


def parse_row(row):
    codename = row['Иденти- фикатор']
    name = row['Название']
    english_name = row['Title']
    kinds = parse_credit_types(row['Тип курса'])
    text_teachers = row['Предлагает в 2022/23']
    authors = row['Автор программы']
    if text_teachers == '':
        text_teachers = authors
    semesters = parse_semesters(row['Для кого в 21/22 и семестры'])

    thematic_name = row['Раздел'].replace(' ', '').split(',')[0]

    languages = [
        lang for lang in row['Язык'].replace(' ', '').split(',')
        if len(lang) > 0
    ]
    description = row['Аннотация']
    english_description = row['Abstract']

    if len(languages) == 0 or len(semesters) == 0 or len(kinds) == 0 or len(codename) == 0:
        message = f'Incorrect row:\n {row}'
        # logger.error(message)
        return None, message

    if len(row['предлагаем? (если "да", то пустое место)']) != 0:
        message = f'This course is not presenting {row}'
        # logger.warning(message)
        return None, ''


    thematic, created = ElectiveThematic.objects.get_or_create(
        short_name=thematic_name,
    )
    if created:
        thematic.name = generate_random_error_name()
        thematic.english_name = generate_random_error_name()
    thematic.save()

    elective, _ = Elective.objects.get_or_create(
        codename=codename,
    )
    elective.thematic = thematic
    elective.name = name
    elective.english_name = english_name
    elective.text_teachers = text_teachers
    elective.description = description
    elective.english_description = english_description
    elective.save()

    for kind, semester, lang in product(kinds, semesters, languages):
        credit_units_kind, _ = CreditUnitsKind.objects.get_or_create(
            short_name=kind,
        )
        elective_kind, _ = ElectiveKind.objects.get_or_create(
            language=lang,
            credit_units_kind=credit_units_kind,
            semester=semester,
        )
        kind_of_elective, _ = KindOfElective.objects.get_or_create(
            elective=elective,
            kind=elective_kind,
        )
        kind_of_elective.exam_possibility = credit_units_kind.default_exam_possibility
        kind_of_elective.save()

    return elective, ''


def delete_old_electives(updated_codenames: list[str]):
    Elective.objects.exclude(codename__in=updated_codenames).delete()


def parse_elective_table(fin):
    reader = csv.DictReader(fin)

    codenames: list[str] = []
    report = []
    for row in reader:
        elective, report_messages = parse_row(row)
        if report_messages != '':
            report.append(report_messages)
        if elective is not None:
            codenames.append(elective.codename)
    delete_old_electives(codenames)
    return report


def run_with_local_table(path: str):
    with open(path, 'r', encoding='utf-8') as fin:
        parse_elective_table(fin)
