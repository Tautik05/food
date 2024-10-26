from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
import requests
from .firebase import send_location_to_firebase
import logging
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .firebase import update_firebase_order
from django.db.models import Q
import os
from dotenv import load_dotenv
load_dotenv()


class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


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



def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'confirmation.html', {'order': order})


def order_cancellation(request):
    return render(request, 'cancel.html')  # Create an HTML template for cancellation

@login_required
def delete_food(request, food_id):
    inventory_item = get_object_or_404(FoodInventoryRecord, id=food_id)
    inventory_item.delete()  # Remove the item from the inventory
    return redirect('manage_inventory')  # Redirect back to the inventory page


def deliverypartner_dashboard(request):
    # Ensure the user is authenticated and is a delivery partner
    if request.user.is_authenticated and request.user.role == 'deliverypartner':
        orders = Order.objects.filter(delivery_partner=request.user)
        firebase_config = {
            'apiKey': os.getenv("FIREBASE_API_KEY"),
            'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN"),
            'databaseURL': os.getenv("FIREBASE_DATABASE_URL"),
            'projectId': os.getenv("FIREBASE_PROJECT_ID"),
            'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET"),
            'messagingSenderId': os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            'appId': os.getenv("FIREBASE_APP_ID"),
            'measurementId': os.getenv("FIREBASE_MEASUREMENT_ID"),
        }


        return render(request, 'del-partner-dashboard.html', {'orders': orders,'firebase_config': firebase_config})
    
    else:
        messages.error(request, 'You need to log in as a delivery partner to access this page.')
        return redirect('login_page')  # Redirect to login if the user is not authenticated



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

            # Update or create the delivery partner's location
            location, created = DeliveryPartnerLocation.objects.update_or_create(
                user=user,
                defaults={'latitude': latitude, 'longitude': longitude}
            )

            return JsonResponse({'message': 'Location updated successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



def update_location_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            partner_id = request.user.id  # Assuming the user is authenticated and is a delivery partner

            if latitude and longitude:
                # Send the location to Firebase
                send_location_to_firebase(partner_id, latitude, longitude)
                return JsonResponse({'message': 'Location updated successfully.'})
            else:
                return JsonResponse({'error': 'Invalid location data.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)




def get_delivery_partner_location(request, order_id):
    if request.user.is_authenticated:
        try:
            # Get the order with the given order_id
            order = Order.objects.get(id=order_id, customer=request.user)
            if order.delivery_partner:
                # Get the location of the assigned delivery partner
                location = DeliveryPartnerLocation.objects.get(user=order.delivery_partner)
                return JsonResponse({
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                })
            return JsonResponse({'message': 'No delivery partner assigned yet'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except DeliveryPartnerLocation.DoesNotExist:
            return JsonResponse({'error': 'Location not found'}, status=404)
    return JsonResponse({'error': 'Unauthorized'}, status=401)



# Function to calculate distance using OpenRouteService
def calculate_distance(lat1, lon1, lat2, lon2):
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    ORS_API_URL = os.getenv("ORS_API_URL")

    
    coordinates = [[lon1, lat1], [lon2, lat2]]
    payload = {"coordinates": coordinates}
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(ORS_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Extract the distance in meters
        distance = data['routes'][0]['summary']['distance']
        return distance / 1000  # Return distance in kilometers
    else:
        return None


@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    selected_location = request.session.get('customer_selected_location')

    if not cart_items:
        return redirect('cart')

    # Create the order
    order = Order.objects.create(
        customer=request.user,
        total_price=cart.total_price,
        status='pending',
        payment_status='PAID',
        delivery_address=selected_location
    )

    # Create order items
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            food=cart_item.food_item,
            quantity=cart_item.quantity,
            price=cart_item.price
        )

        inventory_record = FoodInventoryRecord.objects.get(
            inventory__restaurant_owner=cart_item.food_item.restaurant.restaurant_owner,
            food_items=cart_item.food_item
        )
        inventory_record.quantity_sold += cart_item.quantity
        inventory_record.quantity_left = inventory_record.quantity_available - inventory_record.quantity_sold
        if inventory_record.quantity_left == 0:
            inventory_record.delete()  # Delete the record if no quantity is left
        else:
            inventory_record.save()  # Save the updated record

    # Clear the cart
    cart.items.all().delete()

    # Try to assign a delivery partner
    if not assign_closest_delivery_partner(order):
        # If no delivery partner found, set the order status and show a message
        order.status = 'no_delivery_partner'
        order.save()
        messages.error(request, "No delivery partner is currently available to take your order.")
        return redirect('order_cancellation')  # Redirect to the order cancellation page

    # Redirect to the order confirmation page
    return redirect('delivery_map', order_id=order.id, partner_id=order.delivery_partner.id)




def assign_closest_delivery_partner(order, exclude_partners=None):
    restaurant = order.food_items.first().restaurant
    restaurant_latitude = float(restaurant.latitude)
    restaurant_longitude = float(restaurant.longitude)

    exclude_partners = exclude_partners or []

    # Get all delivery partners who are active, not in the excluded list, and not assigned to an ongoing order
    delivery_partners = CustomUser.objects.filter(
        role='deliverypartner',
        is_active=True
    ).exclude(id__in=exclude_partners).exclude(
        # Exclude partners with active (non-delivered) orders
        Q(delivery_orders__status__in=['ontheway', 'preparing', 'pending'])
    )

    closest_partner = None
    min_distance = float('inf')

    # Iterate through delivery partners to find the closest one
    for partner in delivery_partners:
        try:
            location = DeliveryPartnerLocation.objects.get(user=partner)
            distance = calculate_distance(
                lat1=restaurant_latitude, lon1=restaurant_longitude,
                lat2=float(location.latitude), lon2=float(location.longitude)
            )
            if distance < min_distance:
                min_distance = distance
                closest_partner = partner
        except DeliveryPartnerLocation.DoesNotExist:
            continue  # Skip if no location is available

    if closest_partner:
        order.delivery_partner = closest_partner
        order.status = 'ontheway'  # Automatically set status to 'ontheway'
        order.save()

        # Update Firebase with the order details only if a partner is found
        order_details = {
            'order_id': order.id,
            'delivery_address': order.delivery_address,
        }
        print(f"Updating Firebase for partner ID {closest_partner.id} with order details: {order_details}")

        update_firebase_order(closest_partner.id, order_details)

        return True
    else:
        # No delivery partner found, update the order status
        order.status = 'no_delivery_partner'
        order.save()
        return False



def delivery_map(request, order_id, partner_id):
    order = get_object_or_404(Order, id=order_id)

    # Get the customer location from the delivery address (assuming you store latitude/longitude in CustomerLocation)
    customer_location = CustomerLocation.objects.filter(user=order.customer).first()

    # Get the restaurant location by fetching the first restaurant related to the order's food items
    first_food_item = order.food_items.first()
    restaurant = first_food_item.restaurant if first_food_item else None

    # Ensure customer and restaurant data is available
    customer_lat = customer_location.latitude if customer_location else None
    customer_lng = customer_location.longitude if customer_location else None
    restaurant_lat = restaurant.latitude if restaurant else None
    restaurant_lng = restaurant.longitude if restaurant else None

    firebase_config = {
    'apiKey': os.getenv("FIREBASE_API_KEY"),
    'authDomain': os.getenv("FIREBASE_AUTH_DOMAIN"),
    'databaseURL': os.getenv("FIREBASE_DATABASE_URL"),
    'projectId': os.getenv("FIREBASE_PROJECT_ID"),
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET"),
    'messagingSenderId': os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    'appId': os.getenv("FIREBASE_APP_ID"),
    'measurementId': os.getenv("FIREBASE_MEASUREMENT_ID"),
    }

    context = {
        'order': order,
        'partner_id': partner_id,  # Pass the partner ID to the template context
        'customer_lat': customer_lat,
        'customer_lng': customer_lng,
        'restaurant_lat': restaurant_lat,
        'restaurant_lng': restaurant_lng,
        'firebase_config': firebase_config  # Add Firebase config to context
    }
    
    return render(request, 'delivery_map.html', context)




from django.contrib.auth import logout

def logout_view(request):
    if request.user.is_authenticated and request.user.role == 'deliverypartner':
        # Get all accepted orders for the delivery partner
        accepted_orders = Order.objects.filter(delivery_partner=request.user, status='ontheway')

        # Mark each order as delivered and delete it
        for order in accepted_orders:
            order.status = 'delivered'  
            order.delete()  

        # Optionally, you could also choose to delete the location information
        DeliveryPartnerLocation.objects.filter(user=request.user).delete()

    logout(request)  # Logout the user
    return redirect('login_page')  # Redirect to the login page








