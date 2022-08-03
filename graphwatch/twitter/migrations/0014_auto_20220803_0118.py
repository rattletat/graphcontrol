# Generated by Django 3.2.14 on 2022-08-03 01:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0013_alter_account_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='twitter_id',
            field=models.CharField(default=None, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(max_length=15, unique=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
