# Generated by Django 3.2.5 on 2021-10-16 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0012_auto_20211016_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elective',
            name='text_teachers',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
