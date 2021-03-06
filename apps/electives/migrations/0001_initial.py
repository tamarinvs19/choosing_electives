# Generated by Django 3.2.5 on 2021-07-24 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('codename', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(default='')),
                ('max_number_students', models.PositiveIntegerField(default=10)),
                ('min_number_students', models.PositiveIntegerField(default=3)),
            ],
        ),
        migrations.CreateModel(
            name='ElectiveKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_units', models.PositiveSmallIntegerField(choices=[(2, 'SEMINAR'), (3, 'SMALL COURSE'), (4, 'BIG COURSE')])),
                ('language', models.CharField(choices=[('ru', 'russian'), ('en', 'english')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='TeacherOnElective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electives.elective')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.person')),
            ],
        ),
        migrations.CreateModel(
            name='StudentOnElective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_necessary', models.BooleanField(default=False)),
                ('with_examination', models.BooleanField(default=True)),
                ('priority', models.PositiveIntegerField(default=1)),
                ('elective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electives.elective')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.person')),
            ],
        ),
        migrations.CreateModel(
            name='KindOfElective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electives.elective')),
                ('kind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='electives.electivekind')),
            ],
        ),
        migrations.AddField(
            model_name='elective',
            name='kinds',
            field=models.ManyToManyField(related_name='elective_kinds', through='electives.KindOfElective', to='electives.ElectiveKind'),
        ),
        migrations.AddField(
            model_name='elective',
            name='students',
            field=models.ManyToManyField(related_name='student_list', through='electives.StudentOnElective', to='users.Person'),
        ),
        migrations.AddField(
            model_name='elective',
            name='teachers',
            field=models.ManyToManyField(related_name='teacher_list', through='electives.TeacherOnElective', to='users.Person'),
        ),
    ]
