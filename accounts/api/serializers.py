from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError

User = get_user_model()

# Base User Registration Serializer
class BaseRegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'phone', 'address', 'gender', 
            'password1', 'password2'
        ]

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data, user_role):
        user = User(**validated_data, **user_role)
        user.set_password(validated_data['password1'])
        user.save()
        return user


class AdvertiserRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        # Set is_advertiser to True for Advertiser
        return super().create(validated_data, {'is_advertiser': True})


class ContentCreatorRegistrationSerializer(BaseRegistrationSerializer):
    def create(self, validated_data):
        # Set is_content_creator to True for Content Creator
        return super().create(validated_data, {'is_content_creator': True})


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            raise ValidationError("Invalid username or password.")

        attrs['user'] = user  # Attach user to the attributes
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'role']

    def get_role(self, obj: User) -> str:
        if obj.is_content_creator:
            return 'content creator'
        elif obj.is_advertiser:
            return 'advertiser'
        return 'unknown'  # Fallback in case the user doesn't match either role
