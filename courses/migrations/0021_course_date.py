# Generated by Django 2.1.7 on 2019-04-05 09:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0020_auto_20190405_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
