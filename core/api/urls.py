from .views import ReactView
from django.urls import path, include

urlpatterns = [
    path("user/",ReactView.as_view(),name="react")
]