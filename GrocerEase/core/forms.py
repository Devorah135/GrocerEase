# core/forms.py
from django import forms
from .models import ShoppingList

class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['items']  # Replace 'items' with the actual field(s) in your model