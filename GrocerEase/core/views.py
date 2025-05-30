from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .forms import AddItemForm
from .models import ListItem, ShoppingList, Store, StoreItem


@login_required
def shopping_list_view(request):
    shopping_list, _ = ShoppingList.objects.get_or_create(user=request.user)
    total_price = shopping_list.total_price()

    if request.method == 'POST':
        if 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            try:
                shopping_list.delete_item(item_id)
                messages.success(request, "Item removed from your list.")
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
                if new_quantity < 1:
                    messages.error(request, "Quantity must be at least 1.")
                    return redirect('shopping_list')
                list_item = shopping_list.items.get(id=item_id)
                list_item.quantity = new_quantity
                list_item.save()
                messages.success(request, "Quantity updated.")
            except ListItem.DoesNotExist:
                messages.error(request, "Item not found.")
            return redirect('shopping_list')

        else:
            form = AddItemForm(request.POST)
            if form.is_valid():
                store_item = form.cleaned_data['item']
                manual_name = form.cleaned_data['manual_item_name']
                quantity = form.cleaned_data['quantity']

                if not store_item and not manual_name:
                    messages.error(request, "Please select or enter an item name.")
                    return redirect('shopping_list')

                item_name = store_item.name if store_item else manual_name

                # Check if item already exists
                existing = shopping_list.items.filter(name=item_name).first()
                if existing:
                    messages.info(request, f"{item_name} is already in your list.")
                else:
                    list_item = ListItem.objects.create(
                        shopping_list=shopping_list,
                        name=item_name,
                        quantity=quantity
                    )
                    messages.success(request, f"Added {item_name} to your list.")
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
        model = get_user_model()
        fields = ('username', 'password1', 'password2')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('shopping_list')
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
    cheapest_store = min(store_totals, key=store_totals.get) if store_totals else None

    # Optional: Add savings if you calculate it elsewhere
    savings = None  # placeholder if needed

    return render(request, 'compare_prices.html', {
        'store_totals': store_totals,
        'cheapest_store': cheapest_store,
        'savings': savings,
    })


@staff_member_required
def store_inventory_view(request):
    stores = Store.objects.all()
    items = StoreItem.objects.all()

    if request.method == 'POST':
        store_id = request.POST.get('store_id')
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        store = Store.objects.get(id=store_id)
        item = StoreItem.objects.get(id=item_id)

        if action == 'add':
            store.inventory.add(item)
            messages.success(request, f"Added {item.name} to {store.name}.")
        elif action == 'remove':
            store.inventory.remove(item)
            messages.success(request, f"Removed {item.name} from {store.name}.")

    return render(request, 'store_inventory.html', {
        'stores': stores,
        'items': items
    })


def store_item_suggestions(request):
    query = request.GET.get('term', '')
    results = []

    if query:
        matches = StoreItem.objects.filter(name__icontains=query)[:10]
        results = [{'label': item.name, 'value': item.name} for item in matches]

    return JsonResponse(results, safe=False)
