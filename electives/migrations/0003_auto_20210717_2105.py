# Generated by Django 3.2.5 on 2021-07-17 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='elective',
            name='max_number_students',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='elective',
            name='min_number_students',
            field=models.PositiveIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='studentonelective',
            name='priority',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='studentonelective',
            name='with_examenation',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='elective',
            name='credit_unit',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
