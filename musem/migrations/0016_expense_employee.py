# Generated by Django 3.2.8 on 2021-11-02 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0015_inventory_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='employee',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='musem.employee'),
        ),
    ]
