# Generated by Django 4.1 on 2024-02-11 06:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stock", "0005_alter_stockprice_timestamp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stockprice",
            name="timestamp",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
