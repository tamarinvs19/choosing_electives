from django.core.management.base import BaseCommand, CommandError
from apps.parsing.table_parsing import run_with_local_table


class Command(BaseCommand):
    help = 'Run parsing of the local csv-table with course information'

    def add_argument(self, parser):
        parser.add_argument('path', type='str')

    def handle(self, *args, **options):
        path = options['path']
        run_with_local_table(path)
        self.stdout.write(self.style.SUCCESS('Successfully parsed'))
