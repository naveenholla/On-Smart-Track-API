# Generated by Django 4.1.3 on 2022-12-11 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0015_marketscreener_rank"),
        ("users", "0006_stockscreenersectionitem_level_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stockwatchlist",
            name="equity",
        ),
        migrations.CreateModel(
            name="StockWatchlistItem",
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
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("date", models.DateTimeField(auto_now=True)),
                ("enabled", models.BooleanField(default=True)),
                (
                    "equity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="market.equity"
                    ),
                ),
                (
                    "watchlist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.stockwatchlist",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
                "abstract": False,
            },
        ),
    ]
