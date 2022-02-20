from unittest import TestCase

from apps.electives.models import Elective


class TestElective(TestCase):
    def test_create_elective(self):
        new_elective = Elective.objects.create(
            name='Коммутативная алгебра тест',
            english_name='Commutative algebra test',
            codename='CommAlgT',
            description='Описание...',
        )

        self.assertEqual(len(Elective.objects.filter(codename='CommAlgT')), 1)
        new_elective.delete()
