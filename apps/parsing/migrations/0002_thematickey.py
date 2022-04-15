# Generated by Django 3.2.5 on 2022-04-15 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThematicKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=8, unique=True)),
                ('value', models.TextField()),
            ],
        ),
    ]
