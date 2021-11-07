# Generated by Django 3.2.8 on 2021-11-02 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0011_revenue_revenue'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('expense_id', models.IntegerField(primary_key=True, serialize=False)),
                ('cost', models.FloatField(default=0.0)),
                ('date', models.DateField()),
                ('note', models.TextField()),
            ],
            options={
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expense in the museum',
            },
        ),
    ]