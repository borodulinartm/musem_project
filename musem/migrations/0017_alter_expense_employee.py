# Generated by Django 3.2.8 on 2021-11-02 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0016_expense_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='musem.employee'),
        ),
    ]
