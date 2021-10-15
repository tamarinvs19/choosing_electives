from unittest import TestCase

from electives.models import ElectiveThematic


class TestElectiveThematic(TestCase):
    def test_create_thematic(self):
        new_thematic = ElectiveThematic.objects.create(name='Алгебра')

        self.assertEqual(len(ElectiveThematic.objects.all()), 1)
        self.assertEqual(ElectiveThematic.objects.first(), new_thematic)
