from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

from django.http import JsonResponse
import json
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
import json
from decimal import Decimal

class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)





import logging

logger = logging.getLogger(__name__)

def home(request):
    queryset = FoodCategory.objects.all()

    if request.user.is_authenticated and request.user.role == 'customer':
        location_set = CustomerLocation.objects.filter(user=request.user)
        selected_location = request.session.get('customer_selected_location')
        logger.info(f"User {request.user.id} is authenticated. Selected location: {selected_location}")
    else:
        location_set = []
        selected_location = None
        logger.info("User is not authenticated or not a customer")

    restaurants = Restaurant.objects.all().values('restaurant_name', 'restaurant_location', 'latitude', 'longitude', 'restaurant_image')
    logger.info(f"Number of restaurants in database: {restaurants.count()}")

    context = {
        'foodcategory': queryset,
        'locations': location_set,
        'selected_location': selected_location,
        'selected_location_json': json.dumps(selected_location, cls=DecimalEncoder),
        'restaurants_json': json.dumps(list(restaurants), cls=DecimalEncoder)
    }

    return render(request, 'home.html', context)




def save_customer_location_to_session(request):
    try:
        data = json.loads(request.body)
        location = data.get('location')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if location and latitude and longitude:
            request.session['customer_selected_location'] = {
                'address': location,
                'latitude': latitude,
                'longitude': longitude
            }
            return JsonResponse({'success': True, 'message': 'Location saved in session'})
        else:
            return JsonResponse({'success': False, 'error': 'Incomplete location data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




@login_required
def location(request):

    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address')

        if not latitude or not longitude:
            return JsonResponse({'error': 'Could not retrieve location'}, status=400)

        if not address:
            return JsonResponse({'error': 'Address field is required'}, status=400)
        try:
            # Get the currently logged-in user
            user = request.user

            location_obj = CustomerLocation.objects.create(
                user=user,  # Pass the user here
                latitude=latitude,
                longitude=longitude,
                location=address
            )
            location_obj.save()
            return JsonResponse({'message': 'Location saved successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': f'Error saving location: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)





from django.db.models import OuterRef, Subquery

def category_restaurants(request, category_id):
    category = get_object_or_404(FoodCategory, id=category_id)
    selected_location = request.session.get('customer_selected_location')

    # Subquery to get the quantity_left for each food item
    inventory_subquery = FoodInventoryRecord.objects.filter(
        food_items=OuterRef('pk')
    ).values('quantity_left')[:1]  # Limit subquery to return only one value

    # Get all restaurants that have food items in this category and have quantity_left > 0
    restaurants = Restaurant.objects.filter(
        food_products__food_category=category,
        food_products__food_inventory_records__quantity_left__gt=0  # Join with FoodInventoryRecord to ensure quantity_left > 0
    ).distinct()

    # For each restaurant, get the food items in this category with quantity_left > 0
    restaurant_foods = []
    for restaurant in restaurants:
        foods = Food.objects.filter(
            restaurant=restaurant,
            food_category=category
        ).annotate(
            quantity_left=Subquery(inventory_subquery)  # Annotate each food with quantity_left
        ).filter(quantity_left__gt=0)  # Only include food items with available stock

        if foods.exists():
            restaurant_foods.append({
                'restaurant': restaurant,
                'foods': foods
            })

    context = {
        'category': category,
        'restaurant_foods': restaurant_foods,
        'selected_location': selected_location,  # Pass selected location to the template
    }

    return render(request, 'food-category.html', context)



def restaurant_home(request,restaurant_id):

    if request.user.is_authenticated and request.user.role == 'customer':
        restaurant=Restaurant.objects.get(id=restaurant_id)

        selected_location = request.session.get('customer_selected_location')



        inventory_records = FoodInventoryRecord.objects.filter(inventory=restaurant.inventory).select_related('food_items')



        context = {
            'restaurant':restaurant,
            'inventory_records': inventory_records,
            'selected_location': selected_location,  # Pass selected location to the template
            # Pass the inventory records to the template
        }

    return render(request,'restaurant-home.html',context)






@login_required
def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        food_item = get_object_or_404(Food, id=food_id)
        
        # Debug print
        print(f"Adding food item: {food_item.food_name}, Price: {food_item.food_price}")

        existing_cart = Cart.objects.filter(user=request.user).first()

        if existing_cart and existing_cart.restaurant != food_item.restaurant:
            messages.error(request, "You can only add food items from one restaurant at a time. Please clear your cart first.")
            return redirect('restaurant_home', restaurant_id=food_item.restaurant.id)

        cart, created = Cart.objects.get_or_create(user=request.user, restaurant=food_item.restaurant)

        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            food_item=food_item,
            defaults={'price': food_item.food_price}  # Set the price when creating
        )

        if not item_created:
            cart_item.quantity += 1
        
        # Ensure price is always set/updated
        cart_item.price = food_item.food_price
        
        # Debug print
        print(f"Cart item price set to: {cart_item.price}")

        cart_item.save()

        messages.success(request, f"{food_item.food_name} added to your cart!")
        return redirect('view_cart')
    else:
        messages.error(request, "You need to be logged in to add items to your cart.")
        return redirect('customer_login_page')



# View Cart
@login_required
def view_cart(request):
    # Get the cart for the current user
    cart = Cart.objects.filter(user=request.user).first()
    
    # Get all items in the cart using the updated related_name 'items'
    cart_items = cart.items.all() if cart else []
    
    # Calculate the total price of all items in the cart
    cart_total = sum(item.total_price for item in cart_items)
    
    # Pass the cart items and total price to the template
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    
    return render(request, 'cart.html', context)





from django.views.decorators.http import require_POST

@require_POST
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    data = json.loads(request.body)
    action = data.get('action')

    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity = max(0, cart_item.quantity - 1)
    elif action == 'remove':
        cart_item.quantity = 0

    if cart_item.quantity == 0:
        cart_item.delete()
    else:
        cart_item.save()

    # Recalculate cart total
    cart = cart_item.cart
    cart_total = sum(item.total_price for item in cart.items.all())

    return JsonResponse({
        'new_quantity': cart_item.quantity,
        'new_total': cart_item.total_price,
        'cart_total': cart_total,
    })



# Remove Cart Item
@login_required
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()  # Remove the item from the cart
    return redirect('view_cart')


@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.delete()  # Clear the cart by deleting the cart object
        messages.success(request, "Your cart has been cleared.")
    return redirect('home')





def search_restaurant(request):
    search_query = request.GET.get('search_query')

    if search_query:
        try:
            restaurant = Restaurant.objects.get(restaurant_name__icontains=search_query)
            return redirect('restaurant_home', restaurant_id=restaurant.id)
        except Restaurant.DoesNotExist:
            # If no restaurant is found, you can redirect to a search result page or show an error message.
            return render(request, 'error.html', {'search_query': search_query})

    return render(request, 'search_page.html')  # Show the search page if no query is provided





@login_required
def manage_inventory(request):
    # Get the logged-in user (owner)
    owner = request.user

    # Find the restaurant that belongs to this owner
    try:
        restaurant = owner.restaurants.get()  # Assuming one owner has one restaurant
        inventory = restaurant.inventory
        inventory_records = inventory.inventory_records.all()  # Get all food records
    except Restaurant.DoesNotExist:
        return render(request, 'no_restaurant.html')  # Redirect to an error page or message
    
    context = {
        'inventory_records': inventory_records,
        'restaurant_name': restaurant.restaurant_name,
    }
    return render(request, 'owner-home.html', context)



def add_food_item(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        food_description = request.POST.get('food_description')
        food_price = request.POST.get('food_price')
        food_image = request.FILES.get('food_image')
        food_category_name = request.POST.get('food_category')
        food_quantity = int(request.POST.get('food_quantity', 0))  # New field for food quantity

        # Get the logged-in owner's restaurant
        restaurant = get_object_or_404(Restaurant, restaurant_owner=request.user)

        # Check if food category exists, if not, return an error
        try:
            food_category = FoodCategory.objects.get(food_type=food_category_name)
        except FoodCategory.DoesNotExist:
            return JsonResponse({'error': f"Food category '{food_category_name}' does not exist. Please select an existing category."}, status=400)
        

        # Create the new food item for the restaurant
        new_food = Food.objects.create(
            restaurant=restaurant,
            food_category=food_category,
            food_name=food_name,
            food_description=food_description,
            food_price=food_price,
            food_image=food_image,
            quantity=food_quantity  # Set the quantity for the food item

        )
        new_food.save()

        # Create or update the corresponding FoodInventoryRecord for this food item
        restaurant_inventory = restaurant.inventory  # The restaurant's inventory
        FoodInventoryRecord.objects.create(
            inventory=restaurant_inventory,
            food_items=new_food,
            quantity_sold=0,  # default to 0
            quantity_available=food_quantity,  # Set initial available quantity
            quantity_left=food_quantity   
        )
        
        return JsonResponse({'success': 'Food item added successfully!'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)






def update_quantity_available(request, record_id):
    try:
        # Retrieve the FoodInventoryRecord by its ID
        record = FoodInventoryRecord.objects.get(id=record_id)

        # Check if all available items have been ordered (i.e., quantity_left is 0)
        if record.quantity_left == 0:
            record.delete()  # Remove the record from the inventory if none are left
            return JsonResponse({'success': True, 'message': 'Item removed from inventory as it is sold out'})
        else:
            # Otherwise, just save the updated record
            record.save()
            return JsonResponse({'success': True, 'new_quantity_available': record.quantity_available})
    
    except FoodInventoryRecord.DoesNotExist:
        # Handle the case where the record is not found
        return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)





@login_required
def delete_food(request, food_id):
    inventory_item = get_object_or_404(FoodInventoryRecord, id=food_id)
    inventory_item.delete()  # Remove the item from the inventory
    return redirect('manage_inventory')  # Redirect back to the inventory page



from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from home.models import Order, CustomUser, DeliveryPartnerLocation, FoodInventoryRecord, Cart, OrderItem  # Adjust the import according to your project structure

@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    selected_location = request.session.get('customer_selected_location')

    if not cart_items:
        return redirect('cart')

    order = Order.objects.create(
        customer=request.user,
        total_price=cart.total_price,
        status='pending',
        payment_status='PAID',
        delivery_address=selected_location
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            food=cart_item.food_item,
            quantity=cart_item.quantity,
            price=float(cart_item.price)  # Convert price to float
        )

        inventory_record = FoodInventoryRecord.objects.get(
            inventory__restaurant_owner=cart_item.food_item.restaurant.restaurant_owner,
            food_items=cart_item.food_item
        )
        inventory_record.quantity_sold += cart_item.quantity
        inventory_record.quantity_left = inventory_record.quantity_available - inventory_record.quantity_sold
        if inventory_record.quantity_left == 0:
            inventory_record.delete()
        else:
            inventory_record.save()

    cart.items.all().delete()

    assign_closest_delivery_partner(order)

    if order.status == 'no_delivery_partner':
    # Handle order cancellation
        order.delete()  # Remove the order from the database
        return redirect('order_cancellation')  # Redirect to a cancellation page

    return redirect('order_confirmation', order_id=order.id)



# In views.py
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'confirmation.html', {'order': order})

def order_cancellation(request):
    return render(request, 'cancel.html')  # Create an HTML template for cancellation


def deliverypartner_dashboard(request):
    # Ensure the user is authenticated and is a delivery partner
    if request.user.is_authenticated and request.user.role == 'deliverypartner':
        # Get orders assigned to the delivery partner
        orders = Order.objects.filter(delivery_partner=request.user)
        return render(request, 'del-partner-dashboard.html', {'orders': orders})
    
    else:
        messages.error(request, 'You need to log in as a delivery partner to access this page.')
        return redirect('delivery-login/')  # Redirect to login if the user is not authenticated


def update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            # Ensure that the user is a delivery partner
            user = request.user
            if user.role != 'deliverypartner':
                return JsonResponse({'error': 'Only delivery partners can update location'}, status=403)

            # Update or create the delivery partner's location (only keep the latest)
            DeliveryPartnerLocation.objects.update_or_create(
                user=user,
                defaults={'latitude': latitude, 'longitude': longitude}
            )

            return JsonResponse({'message': 'Location updated successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


import requests
from .models import Order, CustomUser, CustomerLocation
from django.contrib.auth import logout



def calculate_distance(lat1, lon1, lat2, lon2):
    ORS_API_KEY = '5b3ce3597851110001cf6248c1d0279576184e8080545073932c8b5c'
    url = f"https://api.openrouteservice.org/v2/directions/driving-car"
    
    # Convert all coordinates to float to avoid JSON serialization issues
    coordinates = [[float(lon1), float(lat1)], [float(lon2), float(lat2)]]
    payload = {"coordinates": coordinates}
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Extract the distance in meters
        distance = data['routes'][0]['summary']['distance']
        return distance / 1000  # Return distance in kilometers
    else:
        return None





def assign_closest_delivery_partner(order, exclude_partners=None):
    restaurant = order.food_items.first().restaurant
    restaurant_latitude = float(restaurant.latitude)  # Convert to float
    restaurant_longitude = float(restaurant.longitude)  # Convert to float

    exclude_partners = exclude_partners or []
    delivery_partners = CustomUser.objects.filter(role='deliverypartner', is_active=True).exclude(id__in=exclude_partners)
    closest_partner = None
    min_distance = float('inf')

    for partner in delivery_partners:

        if Order.objects.filter(delivery_partner=partner, status__in=['ontheway', 'awaiting_confirmation']).exists():
            continue  # Skip this partner if they already have an active order
        try:
            location = DeliveryPartnerLocation.objects.get(user=partner)
            distance = calculate_distance(
                lat1=restaurant_latitude, lon1=restaurant_longitude,
                lat2=float(location.latitude), lon2=float(location.longitude)  # Ensure these are float
            )
            if distance and distance < min_distance:
                min_distance = distance
                closest_partner = partner

        except ObjectDoesNotExist:
            continue

    if closest_partner:
        order.delivery_partner = closest_partner
        order.status = 'awaiting_confirmation'
        order.save()

        # Convert all necessary fields to float before sending
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"delivery_partner_{closest_partner.id}",
            {
                'type': 'send_order_assignment',
                'order_id': order.id,  # Send the ID as a primitive
                'total_price': float(order.total_price)  # Send the total price as a float
            }
        )



        print(f"Assigned delivery partner {closest_partner.name} to order {order.id}")
    else:
        order.status = 'no_delivery_partner'
        order.save()
        print(f"No delivery partner found for order {order.id}. Notifying the customer.")



def handle_accept_decline(request, order_id):
    if request.method == "POST":
        action = request.POST.get('action')
        order = get_object_or_404(Order, id=order_id)

        if order.delivery_partner != request.user:
            return JsonResponse({'error': 'You are not assigned to this order'}, status=403)

        if action == 'accept':
            # order.status = 'in_transit'  # The partner accepts the order
            order.status = 'ontheway'  # The partner accepts the order
            order.save()
            return JsonResponse({'message': 'Order accepted successfully!', 'order_id': order.id})

        elif action == 'decline':
            exclude_partners = [order.delivery_partner.id]
            assign_closest_delivery_partner(order, exclude_partners=exclude_partners)
            return JsonResponse({'message': 'You declined the order, reassigned to next closest partner.'})

        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



from django.db import transaction

def logout_view(request):
    if request.user.is_authenticated and request.user.role == 'deliverypartner':
        with transaction.atomic():  # Start a transaction
            assigned_orders = Order.objects.filter(delivery_partner=request.user, status='ontheway')
            
            for order in assigned_orders:
                order.status = 'delivered'
                order.save()  # Save the updated status to the database
                
                order.delete()  # Delete the order from the database

            DeliveryPartnerLocation.objects.filter(user=request.user).delete()
    
    logout(request)
    return redirect('login_page')


import os
from kafka import KafkaConsumer
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for kafka-python consumer
consumer = KafkaConsumer(
    'delivery_location_updates',  # Topic name
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    security_protocol="SSL",
    ssl_cafile=os.getenv('KAFKA_SSL_CA_PATH'),
    ssl_certfile=os.getenv('KAFKA_SSL_CERT_PATH'),
    ssl_keyfile=os.getenv('KAFKA_SSL_KEY_PATH'),
    group_id=os.getenv('KAFKA_GROUP_ID'),
    auto_offset_reset='earliest',  # Start from the earliest message if no offset exists
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # Deserialize JSON messages
)

# Listen for messages
for message in consumer:
    location_data = message.value
    print(f"Received location update: {location_data}")
