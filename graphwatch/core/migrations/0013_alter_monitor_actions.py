# Generated by Django 3.2.14 on 2022-09-05 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_monitor_actions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitor',
            name='actions',
            field=models.ManyToManyField(related_name='monitors', to='core.Action'),
        ),
    ]