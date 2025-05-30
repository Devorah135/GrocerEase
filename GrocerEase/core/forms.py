# core/forms.py
from django import forms
from .models import ShoppingList, ListItem, StoreItem


class ShoppingListForm(forms.ModelForm):
    class Meta:
        model = ShoppingList
        fields = ['items']  # Replace 'items' with the actual field(s) in your model

class AddItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=StoreItem.objects.all(), required=False, label='Select from list')
    manual_item_name = forms.CharField(max_length=100, required=False, label='Or enter item name')
    quantity = forms.IntegerField(min_value=1, initial=1)

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        manual_name = cleaned_data.get('manual_item_name')

        if not item and not manual_name:
            raise forms.ValidationError("Please select or enter an item.")

        if manual_name:
            try:
                matched_item = StoreItem.objects.get(name__iexact=manual_name.strip())
                cleaned_data['item'] = matched_item  # Use this instead of the empty 'item' field
            except StoreItem.DoesNotExist:
                raise forms.ValidationError(f"'{manual_name}' is not a valid item.")

        return cleaned_data