# Generated by Django 3.2.14 on 2022-08-03 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0021_alter_tweet_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handle',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='twitter.account'),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitter.account'),
        ),
    ]