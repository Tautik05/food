from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login
from home.models import Restaurant
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from home.models import *


def customer_register_page(request):
    if request.method == "POST":
        email = request.POST.get('email_id')
        name= request.POST.get('user_name')
        # role = request.POST.get('role')
        password=request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.info(request, 'user has an account')
            return redirect('customer_register_page')
        
        else:
            user=CustomUser.objects.create(
                email=email,
                name=name,
                role='customer'
            )
            user.set_password(password)
            user.save()
            messages.success(request, 'Account created successfully')
            return redirect('home') 

    return render(request, 'customer-register.html')


# def customer_login_page(request):

#     if request.method == "POST":
#         email = request.POST.get('email_id')
#         role = request.POST.get('role')
#         password=request.POST.get('password')

#         try:
#             customer = CustomUser.objects.get(email=email, role=role)
#             if customer.check_password(password):
#                 login(request, customer)
#                 messages.success(request, 'Login successful!')
#                 return redirect('home')
#             else:
#                 messages.error(request, 'Invalid password. Please try again.')
#                 return redirect('customer-login/')  # Redirect back to login page
#         except CustomUser.DoesNotExist:
#             messages.info(request, 'User does not exist. Please create an account.')
#             return redirect('/customer-register/')

#     return render(request, 'customer-login.html')




def owner_register_page(request):
    if request.method == "POST":
        email = request.POST.get('email_id')
        name= request.POST.get('user_name')
        # role = request.POST.get('role')
        password=request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.info(request, 'user has an account')
            return redirect('owner_register_page')
        
        else:
            user=CustomUser.objects.create(
                email=email,
                name=name,
                role='owner'
            )
            user.set_password(password)
            user.save()
            messages.success(request, 'Account created successfully')
            return redirect('owner_login_page') 

    return render(request, 'owner-register.html')



# def owner_login_page(request):
    
#     if request.method == "POST":
#         email = request.POST.get('email_id')
#         role = request.POST.get('role')
#         password=request.POST.get('password')

#         try:
#             owner = CustomUser.objects.get(email=email, role=role)
#             if owner.check_password(password):
#                 login(request, owner)
#                 messages.success(request, 'Login successful!')
#                 # Check if the owner already has a registered restaurant
#                 if Restaurant.objects.filter(restaurant_owner=owner).exists():
#                     return redirect('manage_inventory')  # Redirect to restaurant home if already registered
#                 else:
#                     return redirect('register_restaurant')
#             else:
#                 messages.error(request, 'Invalid password. Please try again.')
#                 return redirect('owner_login_page')  # Redirect back to login page
#         except CustomUser.DoesNotExist:
#             messages.info(request, 'User does not exist. Please create an account.')
#             return redirect('/owner-register/')

#     return render(request, 'owner-login.html')



def deliverypartner_register_page(request):
    if request.method == "POST":
        email = request.POST.get('email_id')
        name= request.POST.get('user_name')
        # role = request.POST.get('role')
        password=request.POST.get('password')

       
        if CustomUser.objects.filter(email=email).exists():
            messages.info(request, 'user has an account')
            return redirect('delivery-register/')
        
        else:
            user=CustomUser.objects.create(
                email=email,
                name=name,
                role='deliverypartner'
            )
            user.set_password(password)
            user.save()
            messages.success(request, 'Account created successfully')
            login(request, user)  # Log the user in after registration

            return redirect('deliverypartner_dashboard') 

    return render(request, 'deliverypartner-register.html')



# def deliverypartner_login_page(request):

#     if request.method == "POST":
#         email = request.POST.get('email_id')
#         role = request.POST.get('role')
#         password=request.POST.get('password')
  
#         try:
#             customer = CustomUser.objects.get(email=email, role=role)
#             if customer.check_password(password):
#                 login(request, customer)
#                 messages.success(request, 'Login successful!')
#                 return redirect('deliverypartner_dashboard')
#             else:
#                 messages.error(request, 'Invalid password. Please try again.')
#                 return redirect('delivery-login/')  # Redirect back to login page
#         except CustomUser.DoesNotExist:
#             messages.info(request, 'User does not exist. Please create an account.')
#             return redirect('/delivery-register/')

#     return render(request, 'deliverypartner-login.html')




@login_required  # Ensure the user is logged in
def register_restaurant(request):

    # Check if the logged-in user is an owner
    if request.user.role != "owner":
        messages.error(request, 'Only owners can register restaurants')
        return redirect('owner_register_page')  # Redirect to an error page or home

    if request.method == "POST":
        # Get restaurant details from the form
        restaurant_name = request.POST.get('restaurant_name')
        restaurant_location = request.POST.get('restaurant_location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        restaurant_image = request.FILES.get('restaurant_image')


        # Validate latitude and longitude
        try:
            latitude = Decimal(latitude.strip())
            longitude = Decimal(longitude.strip())

        except (InvalidOperation,ValueError):
            messages.error(request, 'Invalid latitude or longitude format.')
            return redirect('register_restaurant')

        try:
             # Create the RestaurantInventory first
            inventory = RestaurantInventory.objects.create(
                restaurant_owner=request.user  # The logged-in user
            )

            # Create the restaurant associated with the logged-in owner
            Restaurant.objects.create(
                restaurant_owner=request.user,  # Use the logged-in user as owner
                restaurant_name=restaurant_name,
                restaurant_location=restaurant_location,
                latitude=latitude,
                longitude=longitude,
                restaurant_image=restaurant_image,
                inventory=inventory
            )

            messages.success(request, 'Restaurant registered successfully!')
            return redirect('restaurant_home')  # Redirect to a success page

        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('register_restaurant')  # Redirect back to restaurant registration on failure

    return render(request, 'restaurantsignup.html')




def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email_id')
        password = request.POST.get('password')

        try:
            # Fetch user only by email
            user = CustomUser.objects.get(email=email)

            # Check password
            if user.check_password(password):
                login(request, user)  # Log the user in
                messages.success(request, 'Login successful!')

                # Redirect based on role
                if user.role == 'customer':
                    return redirect('home')  # Redirect to the customer home page
                elif user.role == 'owner':
                    return redirect('manage_inventory')  # Redirect to the owner home page
                elif user.role == 'deliverypartner':
                    return redirect('deliverypartner_dashboard')  # Redirect to the delivery partner dashboard
                else:
                    messages.error(request, 'Invalid role.')
                    return redirect('login_page')  # Redirect back to the login page
            else:
                messages.error(request, 'Invalid password. Please try again.')
                return redirect('login_page')  # Correct the redirect URL

        except CustomUser.DoesNotExist:
            messages.info(request, 'User does not exist. Please create an account.')
            return redirect('/customer-register/')  # You can change this to redirect to the relevant registration page

    return render(request, 'login.html')  # Render the login template




def logout_page(request):
   logout(request)
   return redirect('home')

def owner_logout_page(request):
   logout(request)
   return redirect('owner_login_page')





# tautik
# tt@gmail.com
# 123456

# TT
# tautik@gmail.com
# 1234



#owner login
#owner
#owner@gmail.com
#123456





