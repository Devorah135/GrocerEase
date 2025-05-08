from django.shortcuts import render
from .models import ShoppingList

# Create your views here.
def shopping_list_view(request):
    shopping_lists = ShoppingList.objects.all()
    return render(request, 'shopping_list.html', {'shopping_lists': shopping_lists})