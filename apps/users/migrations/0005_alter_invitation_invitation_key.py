# Generated by Django 3.2.5 on 2022-04-16 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_invitation_invitation_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='invitation_key',
            field=models.CharField(default='AoW745NJBzqgsRwir~kYHEaby_.GZctU3m1vSV8x', max_length=100),
        ),
    ]