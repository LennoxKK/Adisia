from django.contrib import admin
from .models import User  # Assuming User model is defined in models.py

class UserAdmin(admin.ModelAdmin):
    list_display = [
        "get_full_name",  # Ensure this method is defined in your User model
        "username",
        "email",
        "is_active",
        "is_content_creator",  # Updated from is_student
        "is_advertiser",       # Updated from is_lecturer
     
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_content_creator",  # Updated search fields
        "is_advertiser",       # Updated search fields
     
    ]

    class Meta:
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"

admin.site.register(User, UserAdmin)
