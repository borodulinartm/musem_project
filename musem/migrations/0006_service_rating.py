# Generated by Django 3.2.8 on 2021-11-02 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0005_service'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='rating',
            field=models.FloatField(default=0.0),
        ),
    ]