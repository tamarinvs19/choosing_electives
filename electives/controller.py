import csv
from .models import Elective, BigElective, SmallElective, Seminar


class Controller(object):
    """Controller class contains functions with electives."""
    @staticmethod
    def get_all_electives():
        return Elective.objects.all()

    @staticmethod
    def add_elective(fields):
        model: Elective
        if fields['type'] == 'seminar':
            model = Seminar
        elif fields['type'] == 'small':
            model = SmallElective
        elif fields['type'] == 'big':
            model = BigElective

        elective: Elective = model.object.create(
            name=fields['name'],
            credit_unit=int(fields['credit_unit']),
            description=fields['description'],
            max_number_students=int(fields['max students']),
            min_number_students=int(fields['min students'])
        )
        elective.save()

    @staticmethod
    def add_electives_by_table(table_address: str):
        with open(table_address, 'r') as table:
            reader = csv.DictReader(table, ['name', 'credit unit', 'type', 'description', 'max students', 'min students'])
            for line in reader.readlines():
                Controller.add_elective(line)

