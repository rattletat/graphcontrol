# Generated by Django 3.2.14 on 2022-09-22 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0002_alter_account_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='text',
            field=models.CharField(max_length=1000),
        ),
    ]