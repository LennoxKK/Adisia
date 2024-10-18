from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from course.models import Bid, BidAllocation, BidApplication, Upload, UploadVideo # Updated models
from .serializers import (
    BidSerializer,  # Renamed from CourseSerializer
    BidAllocationSerializer,  # Renamed from CourseAllocationSerializer
    BidApplicationSerializer,
    UploadSerializer,
    UploadVideoSerializer,
    # BidOfferSerializer  # Renamed from CourseOfferSerializer
)

# ViewSet for Bid model (formerly Course)
class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

# ViewSet for BidAllocation model (formerly CourseAllocation)
class BidAllocationViewSet(viewsets.ModelViewSet):
    queryset = BidAllocation.objects.all()
    serializer_class = BidAllocationSerializer
    permission_classes = [IsAuthenticated]

# ViewSet for BidApplication model
class BidApplicationViewSet(viewsets.ModelViewSet):
    queryset = BidApplication.objects.all()
    serializer_class = BidApplicationSerializer
    permission_classes = [IsAuthenticated]

# ViewSet for Upload model (for file uploads related to bids)
class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [IsAuthenticated]

# ViewSet for UploadVideo model (for video uploads related to bids/adverts)
class UploadVideoViewSet(viewsets.ModelViewSet):
    queryset = UploadVideo.objects.all()
    serializer_class = UploadVideoSerializer
    permission_classes = [IsAuthenticated]

# ViewSet for BidOffer model (formerly CourseOffer)

