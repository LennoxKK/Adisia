# Generated by Django 5.1.2 on 2024-10-14 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0003_advert_likes_advert_views"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advert",
            name="likes",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="advert",
            name="views",
            field=models.IntegerField(default=0),
        ),
    ]
