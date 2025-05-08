# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('shopping-list/', views.shopping_list_view, name='shopping_list'),
]