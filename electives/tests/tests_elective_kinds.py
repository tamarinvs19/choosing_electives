from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import ElectiveKind
from ..models import KIND_NAMES, LANG_NAMES


class TestElectiveKinds(TestCase):
    def test_create_kind(self):
        new_kind: ElectiveKind = ElectiveKind.objects.create(credit_units=4, language='ru')

        self.assertEqual(len(ElectiveKind.objects.all()), 1)
        self.assertEqual(ElectiveKind.objects.first(), new_kind)

    def test_modify_kind(self):
        new_kind: ElectiveKind = ElectiveKind.objects.create(credit_units=4, language='ru')

        new_kind.language = 'en'
        new_kind.credit_units = 2
        new_kind.save()

        self.assertEqual(len(ElectiveKind.objects.all()), 1)
        self.assertEqual(new_kind.language, 'en')
        self.assertEqual(new_kind.credit_units, 2)

    def test_modify_kind_free(self):
        _: ElectiveKind = ElectiveKind.objects.create(credit_units=3, language='en')
        new_kind: ElectiveKind = ElectiveKind.objects.create(credit_units=4, language='ru')

        new_kind.credit_units = 3
        self.assertEqual(new_kind.credit_units, 3)

    def test_modify_kind_to_existing(self):
        _: ElectiveKind = ElectiveKind.objects.create(credit_units=3, language='en')
        new_kind: ElectiveKind = ElectiveKind.objects.create(credit_units=4, language='ru')

        new_kind.language = 'en'
        new_kind.credit_units = 3
        with self.assertRaises(ValidationError) as raised:
            new_kind.save()
        self.assertEqual(raised.exception.message,
                         'There is can be only one ElectiveKind instance with the same fields')

    def test_fields_of_kind_big_ru(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=4, language='ru')

        self.assertEqual(new_kind.language, 'ru')
        self.assertEqual(new_kind.credit_units, 4)

    def test_fields_of_kind_small_ru(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=3, language='ru')

        self.assertEqual(new_kind.language, 'ru')
        self.assertEqual(new_kind.credit_units, 3)

    def test_fields_of_kind_elective_ru(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=2, language='ru')

        self.assertEqual(new_kind.language, 'ru')
        self.assertEqual(new_kind.credit_units, 2)

    def test_fields_of_kind_big_en(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=4, language='en')

        self.assertEqual(new_kind.language, 'en')
        self.assertEqual(new_kind.credit_units, 4)

    def test_fields_of_kind_small_en(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=3, language='en')

        self.assertEqual(new_kind.language, 'en')
        self.assertEqual(new_kind.credit_units, 3)

    def test_fields_of_kind_elective_en(self):
        new_kind: ElectiveKind = \
            ElectiveKind.objects.create(credit_units=2, language='en')

        self.assertEqual(new_kind.language, 'en')
        self.assertEqual(new_kind.credit_units, 2)
