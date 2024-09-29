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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from home.views import *
from accounts.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('', home, name='home'),

    path('restaurant/<int:restaurant_id>',restaurant_home,name='restaurant_home'),

    path('inventory/',manage_inventory,name='manage_inventory'),

    path('inventory/update-quantity-available/<int:record_id>/<str:action>/', update_quantity_available, name='update_quantity_available'),


    # URL for updating quantity available    
    # path('inventory/update-quantity-available/<int:record_id>/<str:action>/', update_quantity_available, name='update_quantity_available'),
    
    # path('inventory/update-quantity-sold/<int:record_id>/<str:action>/', update_quantity_sold, name='update_quantity_sold'),

    path('search/', search_restaurant, name='search_restaurant'),


    path('add_food/', add_food_item, name='add_food_item'),
    # path('restaurant/location/',restaurant_location, name='restaurant_location'),
    path('owner/logout',owner_logout_page,name='owner_logout_page'),

    path('save-location/', save_customer_location_to_session, name='save_location_to_session'),

    path('home/location/',location, name='location'),

    path('customer-login/', customer_login_page, name='customer_login_page'),

    path('customer-register/', customer_register_page, name='customer_register_page'),

    path('owner-login/', owner_login_page, name='owner_login_page'),

    path('owner-register/', owner_register_page, name='owner_register_page'),
    
    path('restaurant-register/', register_restaurant, name='register_restaurant'),

    path('delivery-login/', deliverypartner_login_page, name='deliverypartner_login_page'),

    path('delivery-register/', deliverypartner_register_page, name='deliverypartner_register_page'),

    path('logout/', logout_page, name='logout_page'),

    path('admin/', admin.site.urls),
]










if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  




# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]
