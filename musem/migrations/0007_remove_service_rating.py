# Generated by Django 3.2.8 on 2021-11-02 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0006_service_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='rating',
        ),
    ]
