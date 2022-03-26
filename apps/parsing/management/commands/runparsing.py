from django.core.management.base import BaseCommand, CommandError
from apps.parsing.courses_table_parsing import run_parsing


class Command(BaseCommand):
    help = 'Run parsing of the tables with course information'

    def handle(self, *args, **options):
        run_parsing()
        self.stdout.write(self.style.SUCCESS('Successfully parsed'))
