# Generated by Django 5.1.1 on 2024-09-30 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0002_comment_parent_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="title",
            field=models.CharField(default="sample", max_length=255),
            preserve_default=False,
        ),
    ]
