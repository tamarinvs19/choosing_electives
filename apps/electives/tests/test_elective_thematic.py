from unittest import TestCase

from apps.electives.models import ElectiveThematic


class TestElectiveThematic(TestCase):
    def test_create_thematic(self):
        new_thematic = ElectiveThematic.objects.create(
            name='АлгебраТ',
            english_name='AlgebraT',
        )

        self.assertEqual(len(ElectiveThematic.objects.filter(name='АлгебраТ')), 1)
        new_thematic.delete()
