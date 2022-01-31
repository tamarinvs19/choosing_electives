# Generated by Django 3.2.5 on 2022-01-31 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('electives', '0027_auto_20211218_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditUnitsKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_units', models.PositiveSmallIntegerField(default=4)),
                ('russian_name', models.CharField(max_length=50)),
                ('english_name', models.CharField(max_length=50)),
                ('short_name', models.CharField(max_length=1)),
                ('default_exam_possibility', models.CharField(choices=[('+', 'Only with the exam'), ('-', 'Only without the exam'), ('+-', 'With the exam or without the exam')], default='+-', max_length=2)),
            ],
        ),
        migrations.RemoveField(
            model_name='electivekind',
            name='credit_units',
        ),
        migrations.AddField(
            model_name='kindofelective',
            name='exam_possibility',
            field=models.CharField(choices=[('+', 'Only with the exam'), ('-', 'Only without the exam'), ('+-', 'With the exam or without the exam')], default='+-', max_length=2),
        ),
        migrations.AlterField(
            model_name='kindofelective',
            name='elective',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kind_of_elective', to='electives.elective'),
        ),
        migrations.AddField(
            model_name='electivekind',
            name='credit_units_kind',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='electives.creditunitskind'),
        ),
    ]
