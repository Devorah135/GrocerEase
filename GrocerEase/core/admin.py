from django.contrib import admin

# Register your models here.

from .models import Address, StoreItem, ListItem, Store, StoreItemPrice, ShoppingList, User

admin.site.register(Address)
admin.site.register(StoreItem)
admin.site.register(ListItem)
admin.site.register(Store)
admin.site.register(StoreItemPrice)
admin.site.register(ShoppingList)
admin.site.register(User)