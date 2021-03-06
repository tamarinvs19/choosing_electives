# Generated by Django 3.2.5 on 2021-08-26 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0005_alter_electivekind_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='electivekind',
            name='semester',
            field=models.PositiveSmallIntegerField(choices=[(1, 'осенний'), (2, 'весенний')], default=1),
        ),
        migrations.AlterField(
            model_name='electivekind',
            name='credit_units',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Семинар'), (3, 'Малый'), (4, 'Большой')], default=4),
        ),
        migrations.AlterField(
            model_name='electivekind',
            name='language',
            field=models.CharField(choices=[('ru', 'на русском'), ('en', 'на английском')], default='ru', max_length=2),
        ),
    ]
