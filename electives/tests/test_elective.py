from unittest import TestCase

from electives.models import Elective


class TestElective(TestCase):
    def test_create_elective(self):
        new_elective = Elective.objects.create(
            name='Коммутативная алгебра',
            english_name='Commutative algebra',
            codename='CommAlg',
            description='Описание...',
        )

        self.assertEqual(len(Elective.objects.all()), 1)
        self.assertEqual(Elective.objects.first(), new_elective)

