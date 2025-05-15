from email.policy import default

from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from django.db import models

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='USA')

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


class StoreItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def change_price(self, new_price):
        self.price = new_price
        self.save()

    def __str__(self):
        return f"{self.name} (${self.price}) x {self.quantity}"


class ListItem(models.Model):
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)

    def stores_to_prices(self):
        """
        Returns a dictionary of {Store: Price} for this item's prices at different stores.
        """
        return {
            price.store: price.price
            for price in self.item.store_prices.all()
        }

    def __str__(self):
        return self.item.name


class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    inventory = models.ManyToManyField(StoreItem, blank=True)

    def __str__(self):
        return self.name

    def add_to_inventory(self, item):
        self.inventory.add(item)

    def remove_from_inventory(self, item):
        self.inventory.remove(item)

    def clear_inventory(self):
        self.inventory.clear()


class StoreItemPrice(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='store_prices')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} at {self.store.name}: ${self.price}"


class ShoppingList(models.Model):
    items = models.ManyToManyField(ListItem)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        on_delete=models.CASCADE,
        related_name='shopping_list_user',  # Avoid reverse accessor conflicts
        default='default_user'  # Default value for the user field
    )
    name = models.CharField(max_length=255, default="Default List")
    #created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.item.price * item.item.quantity for item in self.items.all())

    def clear_list(self):
        self.items.clear()

    def delete_item(self, item_id):
        self.items.remove(item_id)

    def add_item(self, item):
        self.items.add(item)

    def total_store_prices(self):
        """
        Returns a dict of Store: total_price for the entire shopping list.
        """
        totals = {}
        for list_item in self.items.all():
            item = list_item.item
            for price in item.store_prices.all():
                store = price.store
                total = price.price * item.quantity
                totals[store] = totals.get(store, 0) + total
        return totals

    def __str__(self):
        return f"ShoppingList #{self.id}"


class User(AbstractUser):
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)
    shopping_list = models.OneToOneField('ShoppingList', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_list')
    #username = models.CharField(max_length=150, unique=True, default='default_user')

    def __str__(self):
        return self.username
