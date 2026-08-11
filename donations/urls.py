from django.urls import path
from donations.views import CreateDonationView, ChapaWebhookView, VerifyDonationView

urlpatterns = [
    path("initialize/", CreateDonationView.as_view()),
    path("webhook/", ChapaWebhookView.as_view()),
    path("verify/<str:tx_ref>/", VerifyDonationView.as_view()),
]
