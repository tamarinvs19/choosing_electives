import csv
from .models import Elective, BigElective, SmallElective, Seminar


class Controller(object):
    """Controller class contains functions with electives."""
    @staticmethod
    def get_all_electives():
        return Elective.objects.all()

    @staticmethod
    def add_elective(fields: list[str]):
        model: Elective
        if line['type'] == 'seminar':
            model = Seminar
        elif line['type'] == 'small':
            model = SmallElective
        elif line['type'] == 'big':
            model = BigElective

        elective: Elective = model.object.create(
            name=line['name'],
            credit_unit=int(line['credit_unit']),
            description=line['description'],
            max_number_students=int(line['max students']),
            min_number_students=int(line['min students'])
        )
        elective.save()

    @staticmethod
    def add_electives_by_table(table_address: str):
        with open(table_address, 'r') as table:
            reader = csv.DictReader(table, ['name', 'credit unit', 'type', 'description', 'max students', 'min students'])
            for line in reader.readlines():
                Controller.add_elective(line)

