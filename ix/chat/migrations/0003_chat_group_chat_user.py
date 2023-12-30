# Generated by Django 4.2.6 on 2023-10-08 22:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("chat", "0002_chat_is_test"),
    ]

    operations = [
        migrations.AddField(
            model_name="chat",
            name="group",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="auth.group"
            ),
        ),
        migrations.AddField(
            model_name="chat",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
