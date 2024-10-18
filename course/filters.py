from django.db.models import Q
import django_filters
from .models import Category, Bid, BidAllocation  # Updated model imports

class CategoryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="")

    class Meta:
        model = Category  # Updated to Category
        fields = ["title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change HTML classes and placeholders
        self.filters["title"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Category name"}  # Updated placeholder
        )


class BidAllocationFilter(django_filters.FilterSet):
    content_creator = django_filters.CharFilter(method="filter_by_content_creator", label="")
    bid = django_filters.CharFilter(method="filter_by_bid", label="")

    class Meta:
        model = BidAllocation  # Updated to BidAllocation
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change HTML classes and placeholders
        self.filters["content_creator"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Content Creator"}
        )
        self.filters["bid"].field.widget.attrs.update(
            {"class": "au-input", "placeholder": "Bid"}
        )

    def filter_by_content_creator(self, queryset, name, value):
        return queryset.filter(
            Q(content_creator__first_name__icontains=value) |  # Updated to reference content_creator
            Q(content_creator__last_name__icontains=value)
        ).distinct()  # Ensures unique results

    def filter_by_bid(self, queryset, name, value):
        return queryset.filter(bid__title__icontains=value)  # Updated to bid
