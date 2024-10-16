from django.db import models
from django.conf import settings
from django.db import models
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
    quantity_left=models.IntegerField(default=0)


    def __str__(self):
        return f"{self.food_item.food_name} - Available: {self.quantity_available}, Sold: {self.quantity_sold}"
      



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.username} - {self.restaurant.name}"

    @property
    def total_price(self):
        # total = sum([item.total_price for item in self.cart.items.all()])
        total = sum([item.total_price for item in self.items.all()])
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()  # Store price for each food item
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.food_item.name} - {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ontheway', 'On the Way'),
        ('delivered', 'Delivered'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Paid'),  # After checkout, this will always be set to 'PAID'
    ]

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='orders')
    delivery_partner = models.ForeignKey(CustomUser, null=True, blank=True, related_name='delivery_orders', on_delete=models.SET_NULL)
    food_items = models.ManyToManyField(Food, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.TextField()  # Address for delivery


    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='Item')
    food = models.ForeignKey(Food, on_delete=models.CASCADE,related_name='foods')
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()










# # Create a point object
# point = Point(123.456789, 987.654321)

# # Find all locations within 10 kilometers of the point
# nearby_locations = Location.objects.filter(coordinates__distance_lte=(point, D(km=10)))