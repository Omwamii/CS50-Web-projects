# Generated by Django 4.2.4 on 2023-11-10 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_alter_post_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='posted_by',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
