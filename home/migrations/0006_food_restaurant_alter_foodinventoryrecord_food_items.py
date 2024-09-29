# Generated by Django 5.1 on 2024-09-26 10:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_restaurant_latitude_alter_restaurant_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='restaurant',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='food_products', to='home.restaurant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='foodinventoryrecord',
            name='food_items',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_inventory_records', to='home.food'),
        ),
    ]
