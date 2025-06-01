# core/forms.py
from django import forms
from .models import ShoppingList, ListItem, StoreItem


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['items']  # Replace 'items' with the actual field(s) in your model

class AddItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=StoreItem.objects.all(), required=False, label='Select from list')
    manual_item_name = forms.CharField(max_length=100, required=True, label='Enter item name')
    quantity = forms.IntegerField(min_value=1, initial=1, required=True)

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        manual_name = cleaned_data.get('manual_item_name')

        if not item and not manual_name:
            raise forms.ValidationError("Please select from the list or enter an item name.")

        # ✅ REMOVE the code that checks manual_name against the DB
        # Allow manual_name to come from the API, not your DB

        return cleaned_data