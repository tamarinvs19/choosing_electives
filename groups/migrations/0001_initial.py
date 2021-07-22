# Generated by Django 3.2.5 on 2021-07-17 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Curriculum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='YearOfEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_credit_unit_autumn', models.PositiveSmallIntegerField()),
                ('max_credit_unit_autumn', models.PositiveSmallIntegerField()),
                ('min_credit_unit_spring', models.PositiveSmallIntegerField()),
                ('max_credit_unit_spring', models.PositiveSmallIntegerField()),
                ('course_value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.yearofeducation')),
                ('curriculum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.curriculum')),
            ],
        ),
    ]
