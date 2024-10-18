from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import advertiser_required, content_creator_required
from accounts.models import User  # Assuming User is the only model here
from course.models import Bid, Advert,BidApplication
from course.forms import BidApplicationForm, AdvertForm
from googleapiclient.discovery import build
from django.http import JsonResponse
from django.views import View
from .youtube import youtuber_video_stats, extract_video_id  # Adjust import as necessary
from django.utils import timezone
# ########################################################
# YouTube Video Stats for Adverts
# ########################################################

# class YouTubeVideoStatsView(View):
#     def get(self, request):
#         form = YouTubeLinkForm()
#         return render(request, 'youtube.html', {'form': form})

#     def post(self, request):
#         form = YouTubeLinkForm(request.POST)
#         if form.is_valid():
#             youtube_link = form.cleaned_data['youtube_link']
#             video_id = extract_video_id(youtube_link)

#             if not video_id:
#                 return JsonResponse({'error': 'Invalid YouTube link'}, status=400)
            
#             stats = youtuber_video_stats(video_id)
            
#             if 'error' in stats:
#                 return JsonResponse({'error': stats['error']['message']}, status=400)

#             return JsonResponse(stats)
        
#         return render(request, "youtube.html", {'form': form})

# ########################################################
# Home - View Bids (for Content Creators)
# ########################################################






@login_required
def home_view(request):
    """ Content Creators see available bids and Advertisers/Super Users see top 5 adverts """
    
    if request.user.is_content_creator:
        # Content Creators: Show available bids whose deadline is yet to be reached
        bids = Bid.objects.filter(deadline__gt=timezone.now()).order_by("-updated_date")
        
        # Get the applied bids for the current user
        applied_bids = BidApplication.objects.filter(applicants=request.user).values_list('bid', flat=True)
        
        # Exclude bids that the user has already applied for
        available_bids = bids.exclude(id__in=applied_bids)

        return render(request, "core/index.html", {
            "title": "Available Bids",
            "bids": available_bids,
        })

    elif request.user.is_advertiser or request.user.is_superuser:
        # Advertisers/Super Users: Show top 5 adverts
        top_adverts = Advert.objects.all().order_by("-timestamp")[:5]

        return render(request, "core/index.html", {
            "title": "Top Advertisements",
            "top_adverts": top_adverts,
        })

    # Optional: Redirect or show a not authorized message for other roles
    return render(request, "core/not_authorized.html", {
        "title": "Not Authorized",
        "message": "You are not authorized to view this content."
    })


# ########################################################
# Dashboard (for Advertisers to Track Adverts)
# ########################################################

@login_required
@advertiser_required
def dashboard_view(request):
    """ Advertisers see the progress of their adverts (views and likes) """
    adverts = Advert.objects.filter(advertiser=request.user).order_by("-updated_date")
    return render(request, "core/dashboard.html", {
        "title": "Advert Progress",
        "adverts": adverts,
    })

# ########################################################
# Bid Application (Content Creators)
# ########################################################

@login_required
@content_creator_required
def apply_bid(request, bid_id):
    """ Content Creators can apply for bids """
    bid = get_object_or_404(Bid, id="bid-"+str(bid_id))
    
    if request.method == "POST":
        form = BidApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.content_creator = request.user
            application.bid = bid
            application.save()
            messages.success(request, f"Successfully applied for {bid.title}.")
            return redirect("home")
        else:
            messages.error(request, "Error applying for the bid. Please correct the errors below.")
    else:
        form = BidApplicationForm()

    return render(request, "core/apply_bid.html", {"form": form, "bid": bid})

# ########################################################
# Advert Management (Advertisers)
# ########################################################

@login_required
@advertiser_required
def create_advert(request):
    """ Advertisers can create new adverts """
    if request.method == "POST":
        form = AdvertForm(request.POST)
        if form.is_valid():
            advert = form.save(commit=False)
            advert.advertiser = request.user
            advert.save()
            messages.success(request, "Advert created successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Error creating advert. Please correct the errors below.")
    else:
        form = AdvertForm()

    return render(request, "core/create_advert.html", {"form": form})

@login_required
@advertiser_required
def edit_advert(request, advert_id):
    """ Advertisers can edit their adverts """
    advert = get_object_or_404(Advert, id=advert_id)
    
    if request.method == "POST":
        form = AdvertForm(request.POST, instance=advert)
        if form.is_valid():
            form.save()
            messages.success(request, "Advert updated successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "Error updating advert. Please correct the errors below.")
    else:
        form = AdvertForm(instance=advert)

    return render(request, "core/edit_advert.html", {"form": form, "advert": advert})

@login_required
@advertiser_required
def delete_advert(request, advert_id):
    """ Advertisers can delete their adverts """
    advert = get_object_or_404(Advert, id=advert_id)
    advert.delete()
    messages.success(request, "Advert deleted successfully.")
    return redirect("dashboard")

# ########################################################
# Helper Functions for Form Handling
# ########################################################

def handle_bid_form(request, form, title, redirect_url):
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been saved successfully.")
            return redirect(redirect_url)
    return render(request, "core/bid_form.html", {"form": form, "title": title})

