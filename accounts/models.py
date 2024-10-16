from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin



#admin@gmail.com
#admin
# 12345

class CustomUserManager(BaseUserManager):
    def create_user(self,email,name,password,**extra_fields):
        if not email:
            raise ValueError('the Email field must be set')
        if not password:
            raise ValueError('the Password field must be set')
        if not name:
            raise ValueError('the Name field must be set')
        email=self.normalize_email(email)
        user=self.model(email=email,name=name,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,name, password,email,**extra_fields):
     if not email:
        raise ValueError('The Email field must be set for superusers')

     extra_fields.setdefault('is_staff', True)
     extra_fields.setdefault('is_superuser', True)

     if extra_fields.get('is_staff') is not True:
        raise ValueError('Superuser must have is_staff=True.')
     if extra_fields.get('is_superuser') is not True:
        raise ValueError('Superuser must have is_superuser=True.')

     return self.create_user(email=email, name=name, password=password, **extra_fields)


class CustomUser(AbstractBaseUser,PermissionsMixin):
   email=models.EmailField('email address',unique=True)
   name=models.CharField(max_length=150)
   ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('owner', 'Restaurant Owner'),
        ('deliverypartner', 'Delivery Partner')
    ]
   role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='consumer')
   is_active = models.BooleanField(default=True)
   is_staff = models.BooleanField(default=False)
   date_joined = models.DateTimeField(auto_now_add=True)

   objects=CustomUserManager()

   USERNAME_FIELD='email'
   REQUIRED_FIELDS=['name']



   def __str__(self):
    return self.email
   

class CustomerLocation(models.Model):
   user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="users")
   latitude = models.CharField(max_length=200,default=None)
   longitude = models.CharField(max_length=200,default=None)
   location=models.TextField(default=None)



class DeliveryPartnerLocation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='delivery_location')
    latitude = models.CharField(max_length=200, default=None)
    longitude = models.CharField(max_length=200, default=None)

    def __str__(self):
        return f"{self.user.email} - Location"




