# Generated by Django 3.2.9 on 2021-11-28 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0018_alter_electivethematic_english_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elective',
            name='description',
            field=models.CharField(default='', max_length=200),
        ),
    ]