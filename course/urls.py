from django.urls import path
from .views import (
    CategoryFilterView,
    category_detail,
    apply_for_bid,
    category_add,
    category_edit,
    category_delete,
    bid_single,
    bid_add,
    bid_edit,
    bid_delete,
    BidAllocationFormView,
    BidAllocationFilterView,
    edit_allocated_bid,
    deallocate_bid,
    handle_file_upload,
    handle_file_edit,
    handle_file_delete,
    handle_video_upload,
    handle_video_single,
    handle_video_edit,
    handle_video_delete,
    bid_registration,
    bid_drop,
    user_bid_list,
    add_advert,
    advert_detail,
    edit_advert,
    delete_advert,
    allocate_bid
)

urlpatterns = [
    # Category URLs
    path("", CategoryFilterView.as_view(), name="categories"),
    path("<int:pk>/detail/", category_detail, name="category_detail"),
    path("<str:code>/submit-application/", apply_for_bid, name="sub-application"),
    path("add/", category_add, name="add_category"),
    path("<int:pk>/edit/", category_edit, name="edit_category"),
    path("<int:pk>/delete/", category_delete, name="category_delete"),
    
    # Bid URLs
    path("bid/<slug>/detail/", bid_single, name="bid_detail"),
    path("<int:pk>/bid/add/", bid_add, name="bid_add"),
    path("bid/<slug>/edit/", bid_edit, name="edit_bid"),
    path("bid/delete/<slug>/", bid_delete, name="delete_bid"),
    
    # BidAllocation URLs
    path("bid/assign/", BidAllocationFormView.as_view(), name="bid_allocation"),
    path("bid/allocated/", BidAllocationFilterView.as_view(), name="bid_allocation_view"),
    path("allocated_bid/<int:pk>/edit/", edit_allocated_bid, name="edit_allocated_bid"),
    path("bid/<int:pk>/deallocate/", deallocate_bid, name="bid_deallocate"),
    
    # File uploads URLs
    path("bid/<slug>/documents/upload/", handle_file_upload, name="upload_file_view"),
    path("bid/<slug>/documents/<int:file_id>/edit/", handle_file_edit, name="upload_file_edit"),
    path("bid/<slug>/documents/<int:file_id>/delete/", handle_file_delete, name="upload_file_delete"),
    
    # Video uploads URLs
    path("bid/<slug>/video_tutorials/upload/", handle_video_upload, name="upload_video"),
    path("bid/<slug>/video_tutorials/<video_slug>/detail/", handle_video_single, name="video_single"),
    path("bid/<slug>/video_tutorials/<video_slug>/edit/", handle_video_edit, name="upload_video_edit"),
    path("bid/<slug>/video_tutorials/<video_slug>/delete/", handle_video_delete, name="upload_video_delete"),
    
    # Bid registration
    path("bid/registration/", bid_registration, name="bid_registration"),
    path("bid/drop/", bid_drop, name="bid_drop"),
    path("my_bids/", user_bid_list, name="user_bid_list"),
    
    #Adverts
    path("add-advert/",add_advert,name="add_advert"),
    path("advert_detail/<slug>/",advert_detail,name="advert_detail"),
     path('adverts/<slug:slug>/edit/', edit_advert, name='edit_advert'),  # Edit advert
    path('adverts/<slug:slug>/delete/', delete_advert, name='delete_advert'),  # Delete advert
    
    #Allocate
     path('bids/<slug:bid_slug>/allocate/', allocate_bid, name='allocate_bid'),
]
