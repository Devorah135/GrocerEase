# core/views.py
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect, render
from django.shortcuts import render
from .forms import AddItemForm
from .models import ListItem, ShoppingList

#@login_required
def shopping_list_view(request):
    shopping_list, _ = ShoppingList.objects.get_or_create(user=request.user)
    total_price = shopping_list.total_price()

    if request.method == 'POST':
        if 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            try:
                shopping_list.delete_item(item_id)
            except ListItem.DoesNotExist:
                messages.error(request, "Item not found.")
            return redirect('shopping_list')

        elif 'clear_list' in request.POST:
            shopping_list.clear_list()
            return redirect('shopping_list')

        elif 'edit_quantity' in request.POST:
            item_id = request.POST.get('edit_quantity')
            new_quantity = int(request.POST.get('new_quantity', 1))
            try:
                list_item = shopping_list.items.get(id=item_id)
                list_item.item.quantity = new_quantity
                list_item.item.save()
            except ListItem.DoesNotExist:
                messages.error(request, "Item not found.")
            return redirect('shopping_list')

        else:
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
                messages.error(request, "Invalid form submission.")

    else:
        form = AddItemForm()

    return render(request, 'shopping_list.html', {
        'shopping_list': shopping_list,
        'form': form,
        'total_price': total_price
    })


# Custom UserCreationForm for the custom User model
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()  # Use the custom User model
        fields = ('username', 'password1', 'password2')  # Add other fields if needed

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the new user
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('shopping_list')  # Go straight to shopping list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('shopping_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def compare_prices_view(request):
    shopping_list = ShoppingList.objects.get(user=request.user)
    store_totals = shopping_list.total_store_prices()

    return render(request, 'compare_prices.html', {
        'store_totals': store_totals
    })