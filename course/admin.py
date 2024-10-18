from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Bid, BidApplication, Upload

# Register the models with the admin site
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(BidApplication)
admin.site.register(Upload)

# Optionally, you can unregister the Group model if you don't want it in the admin panel
# admin.site.unregister(Group)
