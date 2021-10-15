from unittest import TestCase

from django.core.exceptions import ValidationError

from electives.models import Elective


class TestElective(TestCase):
    def test_create_elective(self):
        new_elective = Elective.objects.create(
            name='Коммутативная алгебра',
            codename='CommAlg',
            description='Описание...',
        )

        self.assertEqual(len(Elective.objects.all()), 1)
        self.assertEqual(Elective.objects.first(), new_elective)

