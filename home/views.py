from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

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
            quantity_available=food_quantity  # Set initial available quantity
        )
        
        return JsonResponse({'success': 'Food item added successfully!'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)




def update_quantity_available(request, record_id, action):
    try:
        record = FoodInventoryRecord.objects.get(id=record_id)
        if action == 'increase':
            record.quantity_available += 1
        elif action == 'decrease' and record.quantity_available > 0:
            record.quantity_available -= 1

        # Check if the quantity available has dropped to zero
        if record.quantity_available == 0:
            record.delete()  # Remove the record from inventory
        else:
            record.save()

        return JsonResponse({'success': True, 'new_quantity_available': record.quantity_available})
    
    except FoodInventoryRecord.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)






def delete_food(request, id):
   queryset = FoodInventoryRecord.objects.get(id = id)
   queryset.delete()
   return redirect('manage_inventory')

    








#333