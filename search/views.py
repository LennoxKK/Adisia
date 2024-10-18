from itertools import chain
from django.views.generic import ListView
 # Assuming Adverts model exists in core.models
from course.models import Bid,Advert # Assuming Bids model exists in course.models

class SearchView(ListView):
    template_name = "search/search_view.html"
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["count"] = self.count or 0
        context["query"] = self.request.GET.get("q")
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get("q", None)

        if query is not None:
            advert_results = Adverts.objects.search(query)  # Assuming a search method exists
            bid_results = Bids.objects.search(query)  # Assuming a search method exists

            # Combine querysets
            queryset_chain = chain(advert_results, bid_results)
            queryset = sorted(queryset_chain, key=lambda instance: instance.pk, reverse=True)
            self.count = len(queryset)  # Since queryset is actually a list
            return queryset
        return Adverts.objects.none()  # Just an empty queryset as default
