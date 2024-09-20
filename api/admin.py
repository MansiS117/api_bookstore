from django.contrib import admin
from .models import Category , Book  , User
from django.contrib.auth.admin import UserAdmin

from django.utils.html import format_html  # Import 



class MyUserAdmin(UserAdmin):
    list_display = ("email" , "first_name" , "last_name" , "user_type","last_login" , "date_joined" , "is_active") #display this fields in the admin site
    list_display_links = ("email" , "first_name" , "last_name") # can see the details of user by clicking on this fields 
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ("email" ,)

class BookAdmin(admin.ModelAdmin):
    list_display = ("image_tag","title" , "author" , "category" , "price" )
    list_display_links = ("image_tag" , "title")

    def image_tag(self, obj):
        if obj.image:  # Ensure that the image field is not empty
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No image'
    image_tag.short_description = 'Image'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart" , "book" , "quantity")
    list_display_links = ("cart" , "book")


admin.site.register(Category)
admin.site.register(Book , BookAdmin)
# admin.site.register(Ratings)  
