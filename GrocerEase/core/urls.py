# core/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('grocery-api/', views.grocery_products, name='grocery_api'),
    path('suggest-items/', views.store_item_suggestions, name='suggest_items'),
    path('shopping-list/', views.shopping_list_view, name='shopping_list'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('compare-prices/', views.compare_prices_view, name='compare_prices'),
     path('store-inventory/', views.store_inventory_view, name='store_inventory'),
]