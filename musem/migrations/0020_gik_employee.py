# Generated by Django 3.2.8 on 2021-11-02 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musem', '0019_remove_gik_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='gik',
            name='employee',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='musem.employee'),
            preserve_default=False,
        ),
    ]