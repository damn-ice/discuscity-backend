# Generated by Django 3.2 on 2021-04-10 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_post_topic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='user',
            new_name='sender',
        ),
    ]