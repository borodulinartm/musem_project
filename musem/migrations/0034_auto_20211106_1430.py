# Generated by Django 3.2.8 on 2021-11-06 14:30

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0033_auto_20211106_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='date_off',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 11, 6, 14, 30, 15, 605441, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='rating',
            name='date_writing',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 11, 6, 14, 30, 15, 605902, tzinfo=utc)),
        ),
    ]