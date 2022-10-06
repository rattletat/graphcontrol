# Generated by Django 3.2.14 on 2022-10-05 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0007_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_core.group_set+', to='contenttypes.contenttype'),
        ),
    ]
