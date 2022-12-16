# Generated by Django 4.1.3 on 2022-12-15 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_alter_stockscreener_managers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="parent_record",
                to="users.account",
            ),
        ),
    ]
