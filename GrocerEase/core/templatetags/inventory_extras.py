from django import template

register = template.Library()

@register.filter
def get_store_price(store_prices, store):
    return store_prices.filter(store=store).first()
