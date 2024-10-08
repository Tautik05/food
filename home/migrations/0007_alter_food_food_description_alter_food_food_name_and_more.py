# Generated by Django 5.1 on 2024-09-27 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_food_restaurant_alter_foodinventoryrecord_food_items'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='food_description',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='food',
            name='food_name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_location',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_name',
            field=models.CharField(max_length=500),
        ),
    ]
