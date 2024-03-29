# Generated by Django 3.2.8 on 2021-11-03 11:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0031_alter_employee_date_off'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gik',
            old_name='surname',
            new_name='name_author',
        ),
        migrations.AddField(
            model_name='gik',
            name='surname_author',
            field=models.CharField(default='surname author', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='employee',
            name='date_off',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 11, 3, 11, 5, 4, 1265, tzinfo=utc)),
        ),
    ]
