# Generated by Django 3.2.8 on 2021-11-02 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0026_sal_emp'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='expense',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='gik',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='inventory',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='location',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='rating',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='revenue',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='safety',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='sal_emp',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='service',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='session',
            name='is_activate',
            field=models.IntegerField(default=1),
        ),
    ]
