from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db.models import Q
from PIL import Image  # Required for image resizing
from django.utils.crypto import get_random_string
# UserManager with search capabilities
class CustomUserManager(BaseUserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset
    def make_random_password(self, length=8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'):
        """
        Generate a random password for the user.

        Args:
            length (int): Length of the password. Default is 8.
            allowed_chars (str): Characters allowed in the password. Default includes letters, digits, and special characters.

        Returns:
            str: A randomly generated password.
        """
        return get_random_string(length=length, allowed_chars=allowed_chars)


# Genders for the user model
GENDERS = (("M", "Male"), ("F", "Female"))

class User(AbstractUser):
    is_content_creator = models.BooleanField(default=False)
    is_advertiser = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True
    )
    email = models.EmailField(unique=True, blank=True, null=True)  # Ensure unique emails

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.username} (ID: {self.id})"

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_content_creator:
            return "Content Creator"
        elif self.is_advertiser:
            return "Advertiser"
        return "User"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + "default.png"
            return no_picture

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"id": self.id})

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + "default.png":
            self.picture.delete()
        super().delete(*args, **kwargs)
