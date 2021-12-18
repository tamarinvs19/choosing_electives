# Generated by Django 3.2.5 on 2021-12-18 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0026_auto_20211207_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elective',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='elective',
            name='english_description',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='elective',
            name='english_name',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='elective',
            name='name',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
