# Generated by Django 3.2.5 on 2021-12-07 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0007_auto_20211204_2049'),
        ('electives', '0025_auto_20211204_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mandatorythematicinstudentgroup',
            name='student_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mandatory_thematics', to='groups.studentgroup'),
        ),
        migrations.AlterField(
            model_name='mandatorythematicinstudentgroup',
            name='thematic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mandatory_thematics', to='electives.electivethematic'),
        ),
    ]
