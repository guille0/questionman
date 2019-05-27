# Generated by Django 2.1.7 on 2019-04-04 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_auto_20190404_1824'),
        ('users', '0002_auto_20190404_1813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='liked',
            new_name='courses_liked',
        ),
        migrations.AddField(
            model_name='profile',
            name='courses_done',
            field=models.ManyToManyField(blank=True, related_name='done_by', to='courses.Course'),
        ),
        migrations.AddField(
            model_name='profile',
            name='questionnaires_done',
            field=models.ManyToManyField(blank=True, related_name='done_by', to='courses.Questionnaire'),
        ),
    ]