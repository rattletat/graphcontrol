# Generated by Django 3.2.14 on 2022-10-10 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20221005_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='max_delay',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
