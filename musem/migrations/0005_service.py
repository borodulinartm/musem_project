# Generated by Django 3.2.8 on 2021-11-02 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0004_rename_client_id_rating_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='title', max_length=50)),
                ('description', models.TextField(default='description to service')),
                ('cost', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Service in this museum',
            },
        ),
    ]