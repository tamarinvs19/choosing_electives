# Generated by Django 3.2.5 on 2021-07-16 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Elective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('credit_unit', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='BigElective',
            fields=[
                ('elective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='electives.elective')),
            ],
            bases=('electives.elective',),
        ),
        migrations.CreateModel(
            name='Seminar',
            fields=[
                ('elective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='electives.elective')),
            ],
            bases=('electives.elective',),
        ),
        migrations.CreateModel(
            name='SmallElective',
            fields=[
                ('elective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='electives.elective')),
            ],
            bases=('electives.elective',),
        ),
    ]
