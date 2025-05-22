# core/forms.py
from django import forms
from .models import ShoppingList, ListItem, StoreItem


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['items']  # Replace 'items' with the actual field(s) in your model

class AddItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=StoreItem.objects.all(), label="Item")
    quantity = forms.IntegerField(min_value=1, label="Quantity", initial=1)