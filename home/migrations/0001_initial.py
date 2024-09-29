# Generated by Django 5.0.7 on 2024-09-01 21:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_type', models.CharField(max_length=100)),
                ('category_image', models.ImageField(upload_to='img')),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=100)),
                ('food_description', models.CharField(max_length=100)),
                ('food_price', models.IntegerField()),
                ('food_image', models.ImageField(upload_to='img')),
                ('food_stock', models.IntegerField(default=0)),
                ('food_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='foods', to='home.foodcategory')),
            ],
        ),
        migrations.CreateModel(
            name='FoodInventoryRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_sold', models.IntegerField(default=0)),
                ('quantity_available', models.IntegerField(default=0)),
                ('food_items', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_records', to='home.food')),
            ],
        ),
        migrations.CreateModel(
            name='RestaurantInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_items', models.ManyToManyField(related_name='inventories', through='home.FoodInventoryRecord', to='home.food')),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_name', models.CharField(max_length=100)),
                ('restaurant_location', models.CharField(max_length=255)),
                ('restaurant_image', models.ImageField(upload_to='img')),
                ('inventory', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='restaurant', to='home.restaurantinventory')),
            ],
        ),
        migrations.AddField(
            model_name='foodinventoryrecord',
            name='inventory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_records', to='home.restaurantinventory'),
        ),
    ]
