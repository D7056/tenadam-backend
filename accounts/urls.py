from django.urls import path
from .views import RegisterView, DrugImageView,LoginView, MeView, ProviderRegisterView,EditProfile, ProviderListView, CompleteProfileView, DoctorListView

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", LoginView.as_view(), name="login"),
    path('me/', MeView.as_view(), name="me"),
    path('register-provider/', ProviderRegisterView.as_view(), name='register_provider'),
    path("providers/medicine-dealers/", ProviderListView.as_view(), name="medicine-dealer-list"),
    path("providers/doctors/", DoctorListView.as_view(), name="doctor-list"),
path('drug-image/', DrugImageView.as_view(), name='drug_image'),
path('edit/', EditProfile.as_view(), name="edit_profile"),
path('complete-profile/', CompleteProfileView.as_view(), name="complete_profile")]