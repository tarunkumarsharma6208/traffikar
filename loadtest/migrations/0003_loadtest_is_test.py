# Generated by Django 5.0.3 on 2024-11-14 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loadtest', '0002_loadtest_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadtest',
            name='is_test',
            field=models.BooleanField(default=False),
        ),
    ]
