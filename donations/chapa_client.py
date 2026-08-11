import requests
from django.conf import settings

CHAPA_BASE_URL = "https://api.chapa.co/v1"


class ChapaError(Exception):
    pass


def _headers():
    return {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(
    *, amount, currency, email, first_name, last_name, tx_ref, callback_url, return_url
):
    payload = {
        "amount": str(amount),
        "currency": currency,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url,
    }
    response = requests.post(
        f"{CHAPA_BASE_URL}/transaction/initialize",
        json=payload,
        headers=_headers(),
        timeout=15,
    )
    data = response.json()
    if data.get("status") != "success":
        raise ChapaError(data.get("message", "Failed to initialize Chapa transaction"))
    return data["data"]["checkout_url"]


def verify_transaction(tx_ref):
    response = requests.get(
        f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
        headers=_headers(),
        timeout=15,
    )
    return response.json()
