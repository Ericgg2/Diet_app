# Generated by Django 5.1.1 on 2024-09-23 01:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserGoal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "goal_type",
                    models.CharField(
                        choices=[
                            ("Diet", "다이어트"),
                            ("Maintain", "유지"),
                            ("Bulk", "벌크업"),
                        ],
                        max_length=10,
                    ),
                ),
                ("daily_calories", models.FloatField()),
                ("protein_goal", models.FloatField()),
                ("fat_goal", models.FloatField()),
                ("carbs_goal", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("height", models.FloatField()),
                ("weight", models.FloatField()),
                ("age", models.IntegerField()),
                (
                    "gender",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female")], max_length=10
                    ),
                ),
                (
                    "activity_level",
                    models.CharField(
                        choices=[
                            ("sedentary", "좌식"),
                            ("light", "가벼운 활동"),
                            ("moderate", "적당한 활동"),
                            ("very_active", "매우 활동적"),
                            ("extra_active", "매우 활동적인 경우"),
                        ],
                        max_length=20,
                    ),
                ),
                ("bmr", models.FloatField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
