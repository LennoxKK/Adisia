from django.urls import include, path
from rest_framework import routers
from .views import (
    BidViewSet,  # Updated from CourseViewSet
    BidAllocationViewSet,  # Updated from CourseAllocationViewSet
    BidApplicationViewSet,
    UploadViewSet,
    UploadVideoViewSet,
)

app_name = "bids-api"  # Updated namespace for the app

router = routers.DefaultRouter()
router.register(r'bids', BidViewSet)  # Updated from 'courses' to 'bids'
router.register(r'bid-allocations', BidAllocationViewSet)  # Updated from 'course-allocations'
router.register(r'bid-applications', BidApplicationViewSet)
router.register(r'uploads', UploadViewSet)
router.register(r'upload-videos', UploadVideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Other URL patterns...
]
