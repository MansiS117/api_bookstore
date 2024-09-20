from django.db import models
from django.contrib.auth.models  import AbstractUser 
from .manager import CustomUserManager
from django.utils import timezone
# Create your models here.

class TimestampModel(models.Model):
    created = models.DateTimeField(default=timezone.now, editable=False)  # Automatically set when created
    updated_at = models.DateTimeField(default=timezone.now, editable=False)      # Automatically set when updated

    class Meta:
        abstract = True 

class Category(TimestampModel):
    name = models.CharField(max_length= 100)
    # slug = models.SlugField(max_length=100 , unique= True , null = True)
    # cat_image = models.ImageField(upload_to= "media/categories" , blank = True)
        
    def __str__(self):
        return self.name
    
    

USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]

class User(AbstractUser , TimestampModel):
       username = None
       phone_number = models.CharField(max_length=20, blank=True, null=True)
       address = models.TextField(blank=True, null=True)

       
       email = models.EmailField(unique=True) 

       user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')


       USERNAME_FIELD = "email"
       REQUIRED_FIELDS = [ "first_name" , "last_name"]

       objects = CustomUserManager()

       def __str__(self):
            return self.email
 
class Book(TimestampModel):
    title = models.CharField(max_length= 100 , blank = False)
    author = models.CharField(max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category , on_delete= models.SET_NULL , null = True) 
    price =  models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to= "media" , null = True)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default= True)

    def __str__(self):
        return self.title






# class Ratings(models.Model):
#     book = models.ForeignKey(Book , on_delete= models.CASCADE)
#     user = models.ForeignKey(User , on_delete= models.CASCADE )
#     rating = models.PositiveIntegerField()
    