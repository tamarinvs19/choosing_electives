import csv
from .models import Elective, KindOfElective


class Controller(object):
    """Controller class contains functions with electives."""
    @staticmethod
    def get_all_electives():
        return Elective.objects.all()
