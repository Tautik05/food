"""
URL configuration for food project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from home.views import *
from accounts.views import *

from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    
    path('', home, name='home'),

    path('category/<int:category_id>/', category_restaurants, name='category_restaurants'),

    path('restaurant/<int:restaurant_id>',restaurant_home,name='restaurant_home'),

    path('inventory/',manage_inventory,name='manage_inventory'),

    path('delete-food/<int:food_id>/', delete_food, name='delete_food'),

    path('inventory/update-quantity-available/<int:record_id>/', update_quantity_available, name='update_quantity_available'),

    path('search/', search_restaurant, name='search_restaurant'),

    path('cart/', view_cart, name='view_cart'),

    path('cart/add/<int:food_id>/', add_to_cart, name='add_to_cart'),

    path('cart/update/<int:cart_item_id>/', update_cart_item, name='update_cart_item'),

    path('cart/remove/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),

    path('cart/clear/', clear_cart, name='clear_cart'),

    path('checkout/', checkout, name='checkout'),

    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),

    path('delivery-dashboard/', deliverypartner_dashboard, name='deliverypartner_dashboard'),  # Add this line

    path('update_location/', update_location, name='update_location'),

    path('assign-delivery-partner/<int:order_id>/', assign_closest_delivery_partner, name='assign_delivery_partner'),  # Endpoint for assigning closest delivery partner to an order

    path('delivery/accept-decline/<int:order_id>/', handle_accept_decline, name='accept_decline'),

    path('order/cancellation/', order_cancellation, name='order_cancellation'),  # Add this line


    path('add_food/', add_food_item, name='add_food_item'),
    # path('restaurant/location/',restaurant_location, name='restaurant_location'),

    path('save-location/', save_customer_location_to_session, name='save_location_to_session'),

    path('home/location/',location, name='location'),
    
    path('login/', login_page, name='login_page'),

    path('customer-register/', customer_register_page, name='customer_register_page'),

    path('owner-register/', owner_register_page, name='owner_register_page'),
    
    path('restaurant-register/', register_restaurant, name='register_restaurant'),

    path('delivery-register/', deliverypartner_register_page, name='deliverypartner_register_page'),

    path('logout/', logout_page, name='logout_page'),

    path('logout-view/', logout_view, name='logout_view'),

    # path('home/', include('home.urls')),  # Update with your actual app name

    path('admin/', admin.site.urls),
]

from home.routing import websocket_urlpatterns


urlpatterns += websocket_urlpatterns





if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  




# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

# http://127.0.0.1:8000/