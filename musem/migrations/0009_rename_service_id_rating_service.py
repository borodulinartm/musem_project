# Generated by Django 3.2.8 on 2021-11-02 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0008_alter_rating_service_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rating',
            old_name='service_id',
            new_name='service',
        ),
    ]