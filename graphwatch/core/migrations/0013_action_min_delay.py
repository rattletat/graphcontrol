# Generated by Django 3.2.14 on 2022-10-11 16:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20221010_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='min_delay',
            field=models.DurationField(default=datetime.timedelta),
        ),
    ]