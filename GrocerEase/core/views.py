# core/views.py
from django.shortcuts import redirect, render
from .forms import AddItemForm
from .models import ListItem, ShoppingList


def shopping_list_view(request):
    shopping_list, _ = ShoppingList.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            store_item = form.cleaned_data['item']
            quantity = form.cleaned_data['quantity']
            list_item, _ = ListItem.objects.get_or_create(item=store_item)
            list_item.item.quantity = quantity
            list_item.item.save()
            shopping_list.add_item(list_item)
            return redirect('shopping_list')
    else:
        form = AddItemForm()
    return render(request, 'shopping_list.html', {'shopping_list': shopping_list, 'form': form})