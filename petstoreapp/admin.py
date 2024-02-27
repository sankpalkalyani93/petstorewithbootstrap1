from django.contrib import admin
from .models import Pet, Cart, CartItems

# Register your models here.
admin.site.register(Pet)
admin.site.register(Cart)
admin.site.register(CartItems)