# Generated by Django 3.2.14 on 2022-10-05 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0008_accountgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stream',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitter.accountgroup'),
        ),
    ]