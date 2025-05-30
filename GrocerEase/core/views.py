from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .forms import AddItemForm
from .models import ListItem, ShoppingList, Store, StoreItem

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

@login_required
def shopping_list_view(request):
    user = request.user
    shopping_list, _ = ShoppingList.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            quantity = form.cleaned_data['quantity']

            # Get or create the ListItem
            list_item, created = ListItem.objects.get_or_create(item=item)
            if not created:
                list_item.quantity += quantity
            else:
                list_item.quantity = quantity
            list_item.save()

            shopping_list.add_item(list_item)
            return redirect('shopping_list')
        else:
            messages.error(request, "Please enter a valid item.")

    else:
        form = AddItemForm()

    if request.method == 'POST' and 'edit_quantity' in request.POST:
        item_id = request.POST.get('edit_quantity')
        new_quantity = request.POST.get('new_quantity')
        try:
            item = ListItem.objects.get(id=item_id)
            item.quantity = int(new_quantity)
            item.save()
        except (ListItem.DoesNotExist, ValueError):
            pass
        return redirect('shopping_list')

    if request.method == 'POST' and 'delete_item' in request.POST:
        item_id = request.POST.get('delete_item')
        try:
            item = ListItem.objects.get(id=item_id)
            shopping_list.items.remove(item)
        except ListItem.DoesNotExist:
            pass
        return redirect('shopping_list')

    if request.method == 'POST' and 'clear_list' in request.POST:
        shopping_list.clear_list()
        return redirect('shopping_list')

    context = {
        'form': form,
        'shopping_list': shopping_list,
    }
    return render(request, 'shopping_list.html', context)

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

    if not store_totals:
        return render(request, 'compare_prices.html', {
            'sorted_totals': [],
            'cheapest_store': None,
            'savings': None,
        })

    # Sort stores by total price
    sorted_totals = sorted(store_totals.items(), key=lambda x: x[1])
    cheapest_store, cheapest_price = sorted_totals[0]

    savings = None
    if len(sorted_totals) > 1:
        second_cheapest_price = sorted_totals[1][1]
        savings = round(second_cheapest_price - cheapest_price, 2)

    return render(request, 'compare_prices.html', {
        'sorted_totals': sorted_totals,
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
