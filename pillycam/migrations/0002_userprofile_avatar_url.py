# Generated by Django 4.2.6 on 2023-10-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pillycam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]