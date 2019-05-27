# Generated by Django 2.1.7 on 2019-05-27 07:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('users', '0001_initial'), ('users', '0002_auto_20190404_1813'), ('users', '0003_auto_20190404_1824')]

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        # ('courses', '0015_auto_20190404_1758'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses_liked', models.ManyToManyField(blank=True, related_name='liked_by', to='courses.Course')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('courses_done', models.ManyToManyField(blank=True, related_name='done_by', to='courses.Course')),
                ('questionnaires_done', models.ManyToManyField(blank=True, related_name='done_by', to='courses.Questionnaire')),
            ],
        ),
    ]
