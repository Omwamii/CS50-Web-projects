# Generated by Django 4.2.4 on 2023-08-28 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_comment_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['comment_date']},
        ),
    ]
