# Generated by Django 4.2.6 on 2023-11-02 04:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0013_chainedge_source_key_chainedge_target_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="nodetype",
            name="context",
            field=models.CharField(max_length=32, null=True),
        ),
    ]
