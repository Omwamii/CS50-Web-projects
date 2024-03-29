# Generated by Django 4.2.4 on 2023-11-10 13:00

import datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_alter_post_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='liked_by',
            field=models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 10, 13, 0, 44, 196247, tzinfo=datetime.timezone.utc), editable=False),
        ),
    ]
