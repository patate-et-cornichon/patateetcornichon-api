# Generated by Django 2.1.2 on 2018-10-08 14:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0002_auto_20180907_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
