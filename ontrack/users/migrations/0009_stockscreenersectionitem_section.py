# Generated by Django 4.1.3 on 2022-12-11 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0008_rename_screener_stockscreenersectionitem_market_screener_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="stockscreenersectionitem",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="users.stockscreenersection",
            ),
        ),
    ]
