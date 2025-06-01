from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import requests
from base64 import b64encode
import random
from .forms import AddItemForm
from .models import ListItem, ShoppingList, Store, StoreItem
from .models import Store, Address

# === Kroger API Token Helper ===
def get_kroger_token():
    client_id = "grocereaseapp-bbc6fl1b"
    client_secret = "0NYl23r6KbQMRSi262axbzvkVUR-UmV9eYkYWoSh"

    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }

    url = "https://api-ce.kroger.com/v1/connect/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    print(response.status_code, response.text)  # 👈 For debugging
    response.raise_for_status()
    return response.json()["access_token"]

def get_kroger_stores(zip_code="45202", limit=5):
    token = get_kroger_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "filter.zipCode": zip_code,
        "filter.limit": limit
    }
    response = requests.get("https://api-ce.kroger.com/v1/locations", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def save_kroger_stores(zip_code):
    stores = get_kroger_stores(zip_code)
    for s in stores:
        address_data = s['address']
        address = Address.objects.create(
            street=address_data.get('addressLine1', ''),
            city=address_data.get('city', ''),
            state=address_data.get('state', ''),
            zip_code=address_data.get('zipCode', ''),
            country='USA'
        )
        Store.objects.create(
            name=s['name'],
            address=address
        )

def grocery_products(request):
    token = get_kroger_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api-ce.kroger.com/v1/products?filter.term=milk&filter.limit=10", headers=headers)
    data = response.json()
    products = data.get("data", [])
    return render(request, "grocery_api.html", {"products": products})

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

@login_required
def shopping_list_view(request):
    user = request.user
    shopping_list, _ = ShoppingList.objects.get_or_create(user=user)

    if request.method == 'POST' and ('item' in request.POST or 'manual_item_name' in request.POST):
        form = AddItemForm(request.POST)
        products = []
        if form.is_valid():
            item_name = request.POST.get('manual_item_name') or form.cleaned_data['item'].name
            quantity = form.cleaned_data['quantity']

            token = get_kroger_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"https://api-ce.kroger.com/v1/products?filter.term={item_name}&filter.limit=1", headers=headers)
            data = response.json()
            products = data.get("data", [])
            if products:
                product = products[0]
                title = product.get("description", item_name)
                brand = product.get("brand", "Unknown Brand")
                image_url = ""
                if product.get("images"):
                    image = product["images"][0]
                    if image.get("sizes"):
                        image_url = image["sizes"][0].get("url", "")
                price = None
                items = product.get("items", [])
                if items:
                    price_info = product.get("items", [{}])[0].get("price", {})
                    regular_price = price_info.get("regular")
                    promo_price = price_info.get("promo")
                else:
                    price = 5.99

                list_item, created = ListItem.objects.get_or_create(name=title)
                list_item.quantity = quantity if created else list_item.quantity + quantity
                list_item.price = promo_price or regular_price or 5.99
                list_item.regular_price = regular_price
                list_item.promo_price = promo_price
                list_item.brand = brand
                list_item.image_url = image_url
                list_item.save()

                if not shopping_list.items.filter(id=list_item.id).exists():
                    shopping_list.add_item(list_item)
                return redirect('shopping_list')
            else:
                messages.error(request, f"No product found for '{item_name}'")
        else:
            messages.error(request, "Please enter a valid item.")

    elif request.method == 'POST' and 'edit_quantity' in request.POST:
        item_id = request.POST.get('edit_quantity')
        new_quantity = request.POST.get('new_quantity')
        try:
            item = ListItem.objects.get(id=item_id)
            item.quantity = int(new_quantity)
            item.save()
        except (ListItem.DoesNotExist, ValueError):
            messages.error(request, "Failed to update quantity.")
        return redirect('shopping_list')

    elif request.method == 'POST' and 'delete_item' in request.POST:
        item_id = request.POST.get('delete_item')
        try:
            item = ListItem.objects.get(id=item_id)
            shopping_list.items.remove(item)
        except ListItem.DoesNotExist:
            messages.error(request, "Failed to delete item.")
        return redirect('shopping_list')

    elif request.method == 'POST' and 'clear_list' in request.POST:
        shopping_list.clear_list()
        return redirect('shopping_list')

    form = AddItemForm()
    products = []  # ✅ Ensures kroger_results always has a value

    context = {
        'form': form,
        'shopping_list': shopping_list,
        'kroger_results': products
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
    items = shopping_list.items.all()
    real_stores = get_kroger_stores(zip_code="45202")
    store_totals = {}
    missing_items_by_store = {}

    token = get_kroger_token()
    headers = {"Authorization": f"Bearer {token}"}

    for store in real_stores:
        store_name = store.get("name", "Unknown Store")
        store_location_id = store.get("locationId")
        total = 0.0
        missing_items = []

        for item in items:
            response = requests.get(
                "https://api-ce.kroger.com/v1/products",
                headers=headers,
                params={
                    "filter.term": item.get_name(),
                    "filter.locationId": store_location_id,
                    "filter.limit": 1
                }
            )

            product_data = response.json().get("data", [])
            if product_data:
                price_info = product_data[0].get("items", [{}])[0].get("price", {})
                price = price_info.get("promo") or price_info.get("regular")
                if price is not None:
                    total += price * item.quantity
                else:
                    missing_items.append(item.get_name())
            else:
                missing_items.append(item.get_name())

        if not missing_items:
            store_totals[store_name] = round(total, 2)
        else:
            missing_items_by_store[store_name] = missing_items

    if store_totals:
        sorted_totals = sorted(store_totals.items(), key=lambda x: x[1])
        cheapest_store, cheapest_price = sorted_totals[0]
        savings = round(sorted_totals[1][1] - cheapest_price, 2) if len(sorted_totals) > 1 else None
    else:
        sorted_totals = []
        cheapest_store = None
        savings = None

    return render(request, 'compare_prices.html', {
        'sorted_totals': sorted_totals,
        'cheapest_store': {'name': cheapest_store} if cheapest_store else None,
        'savings': savings,
        'missing_items_by_store': missing_items_by_store
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
        token = get_kroger_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f'https://api-ce.kroger.com/v1/products?filter.term={query}&filter.limit=5', headers=headers)
        data = response.json()
        for item in data.get('data', []):
            results.append({'label': item.get('description', 'Item'), 'value': item.get('description', 'Item')})

    return JsonResponse(results, safe=False)

