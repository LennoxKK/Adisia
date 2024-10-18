from django.urls import path
from .views import (
    home_view,
    apply_bid,
    create_advert,
    edit_advert,
    delete_advert,
    dashboard_view,
)

urlpatterns = [
    # Home and Dashboard
    path("", home_view, name="home"),  # Home view for content creators (available bids)
    path("dashboard/", dashboard_view, name="dashboard"),  # Dashboard for advertisers (advert progress)

    # Bid Application (Content Creators)
    path("bid/<int:bid_id>/apply/", apply_bid, name="apply_bid"),

    # Advert Management (Advertisers)
    path("advert/add/", create_advert, name="create_advert"),
    path("advert/<int:advert_id>/edit/", edit_advert, name="edit_advert"),
    path("advert/<int:advert_id>/delete/", delete_advert, name="delete_advert"),
    
    # YouTube Video Stats (for tracking advert performance)
    # path('youtube/video-stats/', YouTubeVideoStatsView.as_view(), name='youtube-video-stats'),
]
