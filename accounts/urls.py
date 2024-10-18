from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import the built-in auth views
from .views import (
    profile, profile_single, admin_panel, profile_update, change_password,
    register_advertiser, ContentCreatorListView, AdvertiserListView, add_bid,
    edit_bid, delete_bid, bid_list_view, validate_username, content_creator_add_view,
    edit_content_creator, delete_content_creator, register_content_creator,
    render_advertiser_pdf_list, render_content_creator_pdf_list, workspace, login_view,LogoutView,workspace_rank
)

urlpatterns = [
    # Login and Logout URLs
    # path('login/', login_view, name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('social-auth/', include('social_django.urls', namespace='social')),
    path("", include("django.contrib.auth.urls")),
    path("admin_panel/", admin_panel, name="admin_panel"),
    path("profile/", profile, name="profile"),
    path("profile/<int:id>/detail/", profile_single, name="profile_single"),
    path("setting/", profile_update, name="edit_profile"),
    path("change_password/", change_password, name="change_password"),

    # Advertisers
    path("advertisers/register/", register_advertiser, name="register_advertiser"),
    path('advertisers/', AdvertiserListView.as_view(), name='advertiser_list'),

    # Content Creators
    path("register-cc/", register_content_creator, name="register_content_creator"),
    path("content-creators/", ContentCreatorListView.as_view(), name="content_creator_list"),
    path('add-content-creator/', content_creator_add_view, name='add_content_creator'),
    path('content-creators/edit/<int:pk>/', edit_content_creator, name='content_creator_edit'),
    path('content-creators/delete/<int:pk>/', delete_content_creator, name='content_creator_delete'),

    # Bids Management
    path("bid/add/", add_bid, name="add_bid"),
    path("bid/<int:pk>/edit/", edit_bid, name="edit_bid"),
    path("bid/<int:pk>/delete/", delete_bid, name="delete_bid"),
    path("bids/", bid_list_view, name="available_bids"),

    path("ajax/validate-username/", validate_username, name="validate_username"),

    # PDF generation paths
    path("create_advertisers_pdf_list/", render_advertiser_pdf_list, name="advertiser_list_pdf"),
    path("create_content_creators_pdf_list/", render_content_creator_pdf_list, name="content_creator_list_pdf"),

    # Workspaces
    path("workspaces/", workspace, name="content_creator_workspace"),
    path("workspaces_rank/", workspace_rank, name="workspace_rank"),
]
