# Generated by Django 3.2.14 on 2022-10-12 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_action_min_delay'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='max_delay',
        ),
        migrations.RemoveField(
            model_name='action',
            name='min_delay',
        ),
    ]
