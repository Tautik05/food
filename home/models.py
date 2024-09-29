from django.db import models

# Create your models here.

from accounts.models import *

class FoodCategory(models.Model):
    food_type=models.CharField(max_length=100)
    category_image=models.ImageField(upload_to="img")


    def __str__(self):
        return self.food_type
    


class Restaurant(models.Model):

    restaurant_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="restaurants")
    restaurant_name = models.CharField(max_length=500)
    restaurant_location = models.CharField(max_length=500)
    restaurant_image = models.ImageField(upload_to="img")
    inventory = models.OneToOneField('RestaurantInventory', on_delete=models.CASCADE, related_name="restaurant")
    # Increase the limits for latitude and longitude
    latitude = models.DecimalField(decimal_places=7, max_digits=9, default=0)
    longitude = models.DecimalField(decimal_places=7, max_digits=10, default=0)


    def __str__(self):
        return self.restaurant_name
   


class Food(models.Model):

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="food_products")  # Link food to a specific restaurant
    food_category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name="foods")
    food_name=models.CharField(max_length=1000)
    food_description=models.CharField(max_length=1000)
    food_price=models.IntegerField()
    quantity = models.IntegerField(default=0)  # Add a quantity field
    food_image=models.ImageField(upload_to="img")



    def __str__(self):
        return self.food_name



class RestaurantInventory(models.Model):
    restaurant_owner=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="onwner")
    food_items=models.ManyToManyField(Food, through='FoodInventoryRecord', related_name="inventories")

    def __str__(self):
        return f"Inventory for {self.restaurant.restaurant_name}"



class FoodInventoryRecord(models.Model):
    inventory = models.ForeignKey(RestaurantInventory, on_delete=models.CASCADE, related_name="inventory_records")
    food_items=models.ForeignKey(Food,on_delete=models.CASCADE,related_name="food_inventory_records")
    quantity_sold=models.IntegerField(default=0)
    quantity_available=models.IntegerField(default=0)


    def __str__(self):
        return f"{self.food_item.food_name} - Available: {self.quantity_available}, Sold: {self.quantity_sold}"
      






# # Create a point object
# point = Point(123.456789, 987.654321)

# # Find all locations within 10 kilometers of the point
# nearby_locations = Location.objects.filter(coordinates__distance_lte=(point, D(km=10)))