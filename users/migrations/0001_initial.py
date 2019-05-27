# Generated by Django 2.1.7 on 2019-05-27 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses_done', models.ManyToManyField(blank=True, related_name='done_by', to='courses.Course')),
                ('courses_liked', models.ManyToManyField(blank=True, related_name='liked_by', to='courses.Course')),
                ('questionnaires_done', models.ManyToManyField(blank=True, related_name='done_by', to='courses.Questionnaire')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]