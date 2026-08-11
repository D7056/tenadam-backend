from django.urls import path

from .views import (
    CreateAvailabilityView,
    UpdateDurationandFeesView,
    MyAvailabilityView,
    DoctorAvailabilityView,
    DoctorBookedSlotsView,
    CreateAppointmentView,
    CreateCustomAvailabilityView,
    MyCustomAvailabilityView,
    DeleteCustomAvailabilityView,
)
urlpatterns=[
    path("availability/", CreateAvailabilityView.as_view(),),
    path("availability/settings", UpdateDurationandFeesView.as_view()),
    path("my-availability/", MyAvailabilityView.as_view()),
    path("custom-availability/", CreateCustomAvailabilityView.as_view()),
    path("my-custom-availability/", MyCustomAvailabilityView.as_view()),
    path("custom-availability/<int:pk>/", DeleteCustomAvailabilityView.as_view()),
    path("doctors/<int:doctor_id>/availability/", DoctorAvailabilityView.as_view()),
    path("doctors/<int:doctor_id>/booked-slots/", DoctorBookedSlotsView.as_view()),
    path("book/", CreateAppointmentView.as_view()),
]
