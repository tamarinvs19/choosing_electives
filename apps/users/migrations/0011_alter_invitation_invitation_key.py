# Generated by Django 3.2.5 on 2022-04-28 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_invitation_invitation_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='invitation_key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
