# Generated by Django 2.1.7 on 2019-04-05 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_remove_course_views'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='questionnaires_completed',
        ),
        migrations.RemoveField(
            model_name='course',
            name='times_completed',
        ),
    ]