import requests
from base64 import b64encode
from django.conf import settings

def get_kroger_token():
    credentials = f"{settings.KROGER_CLIENT_ID}:{settings.KROGER_CLIENT_SECRET}"
    encoded = b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact location.basic"
    }

    response = requests.post("https://api.kroger.com/v1/connect/oauth2/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]