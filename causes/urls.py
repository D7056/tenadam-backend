from django.urls import path
from causes.views import CauseListView, SubmitCauseView, MyCausesView, CauseDetailView

urlpatterns = [
    path("", CauseListView.as_view()),
    path("submit/", SubmitCauseView.as_view()),
    path("mine/", MyCausesView.as_view()),
    path("<int:pk>/", CauseDetailView.as_view()),
]
