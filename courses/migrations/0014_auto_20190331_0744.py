# Generated by Django 2.1.7 on 2019-03-31 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_auto_20190330_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='choices',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]