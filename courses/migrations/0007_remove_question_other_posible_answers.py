# Generated by Django 2.1.7 on 2019-03-28 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20190328_0930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='other_posible_answers',
        ),
    ]
