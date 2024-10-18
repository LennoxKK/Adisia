from django.db.models import Q
import django_filters
from .models import User  # Ensure that you have the correct User model imported

class AdvertiserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="exact", label="")
    name = django_filters.CharFilter(method="filter_by_name", label="")
    email = django_filters.CharFilter(lookup_expr="icontains", label="")

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change HTML classes and placeholders
        self.filters["username"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Advertiser ID No."}
        )
        self.filters["name"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Name"}
        )
        self.filters["email"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Email"}
        )

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )


class ContentCreatorFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="exact", label="")
    name = django_filters.CharFilter(method="filter_by_name", label="")
    email = django_filters.CharFilter(lookup_expr="icontains", label="")

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change HTML classes and placeholders
        self.filters["username"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Content Creator ID No."}
        )
        self.filters["name"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Name"}
        )
        self.filters["email"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Email"}
        )

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )
