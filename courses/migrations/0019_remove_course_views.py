# Generated by Django 2.1.7 on 2019-04-04 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_remove_course_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='views',
        ),
    ]
