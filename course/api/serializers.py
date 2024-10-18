from rest_framework import serializers
from course.models import Bid, BidAllocation, BidApplication, Upload, UploadVideo

# Serializer for Bid model (renamed from Course)
class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['slug', 'title', 'description', 'category', 'creator', 'updated_date', 'deadline']

# Serializer for BidAllocation model (renamed from CourseAllocation)
class BidAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidAllocation
        fields = ['advertiser', 'bid', 'content_creator', 'allocation_date']

# Serializer for BidApplication model
class BidApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidApplication
        fields = ['applicants', 'bid', 'application_date']

# Serializer for Upload model (used for file uploads related to bids)
class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['title', 'bid', 'file', 'updated_date', 'upload_time']

# Serializer for UploadVideo model (used for video uploads related to bids/adverts)
class UploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = ['title', 'slug', 'bid', 'video', 'summary', 'timestamp']


