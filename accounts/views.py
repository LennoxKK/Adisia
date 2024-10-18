from django.http.response import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django_filters.views import FilterView
from .decorators import admin_required,advertiser_required
from .forms import (
    ContentCreatorAddForm,
    AdvertiserAddForm,
    ProfileUpdateForm,
)
from django.db.models import F
from decouple import config
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import DatabaseError
from django.utils.decorators import method_decorator  # Add this import
from course.models import Bid,Advert
from course.forms import BidUpdateForm,BidAddForm,AdvertForm
from .models import User
from .filters import ContentCreatorFilter,AdvertiserFilter
from core.youtube import get_youtube_video_stats
# To generate pdf from template
from django.template.loader import get_template
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)

def register_advertiser(request):
    if request.method == "POST":
        form = AdvertiserAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Advertiser account created successfully.")
            return redirect('login')
        else:
            messages.error(request, "Please fill all fields correctly.")
    else:
        form = AdvertiserAddForm()
        
    return render(request, "accounts/add_advertiser.html", {"form": form})

def register_content_creator(request):
    if request.method == "POST":
        form = ContentCreatorAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Content Creator account created successfully.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = ContentCreatorAddForm()

    return render(request, "accounts/add_content_creator.html", {"form": form})


@login_required
def profile(request):
    if request.user.is_advertiser:
        bids = Bid.objects.filter(creator=request.user)
        return render(request, "accounts/profile.html", {
            "title": request.user.get_full_name,
            "bids": bids,
        })
    elif request.user.is_content_creator:
        adverts = Advert.objects.filter(creator=request.user)
        return render(request, "accounts/profile.html", {
            "title": request.user.get_full_name,
            "adverts": adverts,
        })
    else:
        return redirect("home")

def render_to_pdf(template_name, context):
    """Renders a given template to PDF format."""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="profile.pdf"'
    
    template = render_to_string(template_name, context)
    pdf = pisa.CreatePDF(template, dest=response)
    if pdf.err:
        return HttpResponse("We had some problems generating the PDF")

    return response

@login_required
def render_content_creator_pdf_list(request):
    content_creators = User.objects.filter(is_content_creator=True)  # Adjust this query if necessary
    template_path = "pdf/content_creator_list.html"  # Path to your PDF template
    context = {"content_creators": content_creators}
    response = HttpResponse(content_type="application/pdf")  # Set content type to PDF
    response["Content-Disposition"] = 'filename="content_creator_list.pdf"'  # Set file name for the PDF

    # Find the template and render it
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If there are errors, return an error message
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    
    return response

@login_required
def render_advertiser_pdf_list(request):
    advertisers = User.objects.filter(is_advertiser=True)  # Adjust this query if necessary
    template_path = "pdf/advertiser_list.html"  # Path to your PDF template
    context = {"advertisers": advertisers}
    response = HttpResponse(content_type="application/pdf")  # Set content type to PDF
    response["Content-Disposition"] = 'filename="advertiser_list.pdf"'  # Set file name for the PDF

    # Find the template and render it
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If there are errors, return an error message
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    
    return response

@login_required
@admin_required
def profile_single(request, id):
    user = get_object_or_404(User, pk=id)

    if request.GET.get("download_pdf"):
        context = {
            "title": user.get_full_name,
            "user": user,
        }
        return render_to_pdf("pdf/profile_single.html", context)

    context = {
        "title": user.get_full_name,
        "user": user,
    }
    return render(request, "accounts/profile_single.html", context)

@login_required
@admin_required
def admin_panel(request):
    return render(request, "setting/admin_panel.html", {"title": request.user.get_full_name})

@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "setting/profile_info_change.html", {
        "title": "Setting",
        "form": form,
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "setting/password_change.html", {
        "form": form,
    })

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
@advertiser_required
def add_bid(request):
    # Initialize the form with the current user
    form = BidAddForm(request.POST or None, user=request.user)  # Pass the current user to the form

    if request.method == "POST":
        try:
            if form.is_valid():
                # The creator is already set in the form's __init__ method
                form.save()  # Save the form, which includes the creator
                messages.success(request, "Bid has been created successfully.")
                return redirect("user_bid_list")
            else:
                # Capture and display form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    # Render the form in the template
    return render(request, "course/bid_add.html", {"title": "Add Bid", "form": form})



@login_required
@admin_required
def edit_bid(request, pk):
    bid = get_object_or_404(Bid, pk=pk)
    if request.method == "POST":
        form = BidUpdateForm(request.POST, instance=bid)
        if form.is_valid():
            form.save()
            messages.success(request, "Bid has been updated.")
            return redirect("bid_list")
        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = BidUpdateForm(instance=bid)

    return render(request, "accounts/edit_bid.html", {
        "title": "Edit Bid",
        "form": form,
    })

@login_required
@admin_required
def delete_bid(request, pk):
    bid = get_object_or_404(Bid, pk=pk)
    bid.delete()
    messages.success(request, "Bid has been deleted.")
    return redirect("bid_list")

# ########################################################
# Content Creator views
# ########################################################



@login_required
@admin_required
def content_creator_add_view(request):
    try:
        if request.method == "POST":
            form = ContentCreatorAddForm(request.POST,request.FILES)
            if form.is_valid():
                print(form)
                form.save()
                messages.success(request, "Content Creator account created successfully.")
                return redirect("content_creator_list")  # Redirect to the list view on success
            else:
                messages.error(request, "Correct the error(s) below.")
                return redirect(reverse("home"))  # Redirect to home if the form is invalid
        else:
            form = ContentCreatorAddForm()
        
    except Exception as e:
        # Log the exception if necessary, e.g., using logging
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect(reverse("home"))  # Redirect to home in case of an exception

    return render(request, "accounts/add_content_creator.html", {
        "title": "Add Content Creator",
        "form": form
    })
    

@login_required
@admin_required
def edit_content_creator(request, pk):
    try:
        content_creator = get_object_or_404(User, is_content_creator=True, pk=pk)
        
        if request.method == "POST":
            form = ProfileUpdateForm(request.POST, request.FILES, instance=content_creator)
            if form.is_valid():
                form.save()
                messages.success(request, "Content Creator has been updated.")
                return redirect("content_creator_list")
            else:
                messages.error(request, "Please correct the error below.")
        else:
            form = ProfileUpdateForm(instance=content_creator)
        
        return render(request, "accounts/edit_content_creator.html", {
            "title": "Edit Content Creator",
            "form": form,
        })
    
    except Exception as e:
        # Optionally log the error here
        messages.error(request, "An unexpected error occurred. Redirecting to home.")
        return redirect("home")  # Adjust this to your actual home URL name


def login_view(request):
    # Redirect to social login (Google OAuth2)
    return redirect('social:begin', backend='google-oauth2')

@login_required
@admin_required
def advertiser_add_view(request):
    form = AdvertiserAddForm()  # Initialize the form

    try:
        if request.method == "POST":
            form = AdvertiserAddForm(request.POST, request.FILES)  # Include request.FILES for file uploads
            if form.is_valid():
                form.save()  # Save the form if valid
                messages.success(request, "Advertiser account created successfully.")
                return redirect("advertiser_list")  # Redirect to the list view on success
            else:
                messages.error(request, "Correct the error(s) below.")
                # Render the same template with the form to display validation errors
                return render(request, "advertiser_add.html", {"form": form})

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect(reverse("home"))  # Redirect to home in case of an exception

    # If GET request, render the form for the first time
    return render(request, "acoounts/add_advertiser.html", {"form": form})


@method_decorator([login_required, admin_required], name="dispatch")
class ContentCreatorListView(FilterView):
    queryset = User.objects.filter(is_content_creator=True)
    filterset_class = ContentCreatorFilter
    template_name = "accounts/content_creators_list.html"
    paginate_by = 10

    def get_queryset(self):
        try:
            # Attempt to retrieve the queryset; if there's an issue, handle it here.
            return super().get_queryset()
        except Exception as e:
            # Capture the error message and redirect to home
            messages.error(self.request, f"An error occurred while fetching content creators: {str(e)}")
            return redirect('home')  # Redirect to the home page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Content Creators"
        return context


@method_decorator([login_required, admin_required], name="dispatch")
class AdvertiserListView(FilterView):
    filterset_class = AdvertiserFilter  # Filter class for searching and filtering advertisers
    template_name = "accounts/advertiser_list.html"  # Template to render
    paginate_by = 10  # Pagination limit

    def get_queryset(self):
        try:
            # Attempt to retrieve the queryset for advertisers
            return User.objects.filter(is_advertiser=True)
        except Exception as e:
            # Log the exception or handle it as needed
            messages.error(self.request, "An error occurred while fetching advertisers. Please try again.")
            return redirect('home')  # Redirect to the home page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Advertisers"  # Title for the page context
        return context

@login_required
@admin_required
def delete_content_creator(request, pk):
    try:
        content_creator = get_object_or_404(User, pk=pk)
        content_creator.delete()
        messages.success(request, "Content Creator has been deleted.")
    except Exception as e:  # Catch any exception that occurs
        messages.error(request, f"An error occurred while deleting the content creator: {str(e)}")
    
    return redirect("home")  # Redirect to the home page



@login_required
def bid_list_view(request):
    try:
        # Fetch all bids
        bids = Bid.objects.all()

        # Check if bids exist
        if not bids:
            messages.warning(request, "No bids available.")
            return render(request, 'course/user_bid_list.html', {'bids': bids})

        # Render the template with the bids
        return render(request, 'course/user_bid_list.html', {'bids': bids})

    except Exception as e:
        # Log the exception if needed (optional)
        print(f"Error retrieving bids: {e}")  # For debugging; consider using logging instead
        messages.error(request, "An error occurred while retrieving bids."+"-->"+str(e))
        return redirect('home')  # Redirect to the home page




@login_required
def workspace(request):
    try:
        # Fetch adverts created by the logged-in content creator, ordered by most recent
        adverts = Advert.objects.filter(creator=request.user).order_by('-timestamp')
    except DatabaseError as db_err:
        # Specific handling for database errors
        messages.error(request, "An error occurred while fetching adverts from the database.")
        adverts = []  # Return an empty list if there's a database error
        print(f"Database error: {db_err}")  # Log the error for debugging purposes

    paginator = Paginator(adverts, 10)  # Show 10 adverts per page
    page_number = request.GET.get('page')

    try:
        # Handle pagination errors
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger as page_err:
        # If the page number is not an integer, load the first page
        messages.error(request, "The page number is not valid, loading the first page.")
        page_obj = paginator.page(1)
        print(f"Page number error (not an integer): {page_err}")  # Log the error
    except EmptyPage as empty_err:
        # If the page number is out of range, load the last page
        messages.warning(request, "The page you are trying to access is empty, loading the last page.")
        page_obj = paginator.page(paginator.num_pages)
        print(f"Empty page error: {empty_err}")  # Log the error
    except Exception as general_err:
        # Handle any other exceptions that might occur
        messages.error(request, "An unexpected error occurred while loading the adverts.")
        page_obj = paginator.page(1)  # Load the first page as a fallback
        print(f"General pagination error: {general_err}")  # Log the general error

    # Initialize an empty list to store video stats
    video_stats = []

    # Fetch views and likes for each advert
    for advert in page_obj:
        if advert.youtube_link:  # Check if the advert has a YouTube link
            stats = get_youtube_video_stats(advert.youtube_link, config("YOU_TUBE_API_KEY"))  # Replace with your actual API key
            views = stats.get('views', 0)
            likes = stats.get('likes', 0)

            # Handle 'N/A' responses and set advert properties
            advert.views = 0 if views == "N/A" or (isinstance(views, str) and not views.isdigit()) else int(views)
            advert.likes = 0 if likes == "N/A" or (isinstance(likes, str) and not likes.isdigit()) else int(likes)
            advert.save()

            # Calculate total score and append to video stats
            total = advert.views + advert.likes
            video_stats.append({
                'title': advert.title,
                'views': advert.views,
                'likes': advert.likes,
                'total': total,  # Store the total for sorting
            })

    # Sort the video_stats list based on total views and likes in descending order
    video_stats.sort(key=lambda x: x['total'], reverse=True)

    # If there are video stats, take the first one for the context
    top_video_stat = video_stats[0] if video_stats else {}

    context = {
        'page_obj': page_obj,
        'video_stats': top_video_stat,  # Add sorted video stats to the context
    }

    return render(request, 'course/workspace.html', context)


@login_required
def workspace_rank(request):
    try:
        if request.user.is_advertiser:
            # Fetch adverts linked to bids created by the advertiser
            adverts = Advert.objects.filter(bid__creator=request.user).order_by('-timestamp')

            # Check if there are no adverts for the advertiser
            if not adverts.exists():
                messages.info(request, "No adverts linked to your bids are allocated so far.")
                adverts = []  # Return an empty list if no adverts are found
        else:
            # Fetch only adverts created by content creators, ordered by most recent
            adverts = Advert.objects.filter(creator__is_content_creator=True).order_by('-timestamp')
    except DatabaseError as db_err:
        messages.error(request, "An error occurred while fetching adverts from the database.")
        adverts = []  # Return an empty list if there's a database error
        print(f"Database error: {db_err}")  # Log the error for debugging purposes

    # Create a dictionary to hold the top video stats for each creator
    top_video_stats = {}

    # Fetch views and likes for each advert
    for advert in adverts:
        if advert.youtube_link:  # Check if the advert has a YouTube link
            stats = get_youtube_video_stats(advert.youtube_link, config("YOU_TUBE_API_KEY"))  # Replace with your actual API key
            views = stats.get('views', 0)
            likes = stats.get('likes', 0)

            # Handle 'N/A' responses and set advert properties
            advert.views = 0 if views == "N/A" or (isinstance(views, str) and not views.isdigit()) else int(views)
            advert.likes = 0 if likes == "N/A" or (isinstance(likes, str) and not likes.isdigit()) else int(likes)
            advert.save()

            # Create a total score for sorting
            total = advert.views + advert.likes
            
            # Capture the creator's name
            creator_id = advert.creator.id
            first_name = advert.creator.first_name or ""  # Default to empty if None
            last_name = advert.creator.last_name or ""  # Default to empty if None
            creator_name = f"{first_name} {last_name}".strip()  # Concatenate and remove extra spaces

            # If this advert's creator already has a recorded video, check if the current advert is better
            if creator_id in top_video_stats:
                # Update if the current advert has a higher total
                if total > top_video_stats[creator_id]['total']:
                    top_video_stats[creator_id] = {
                        'name': creator_name,  # Add creator's full name
                        'title': advert.title,
                        'views': advert.views,
                        'likes': advert.likes,
                        'total': total,
                        'youtube_link': advert.youtube_link,
                    }
            else:
                # Otherwise, create a new entry for this creator
                top_video_stats[creator_id] = {
                    'name': creator_name,  # Add creator's full name
                    'title': advert.title,
                    'views': advert.views,
                    'likes': advert.likes,
                    'total': total,
                    'description':advert.description,
                    'bid':advert.bid.title,
                    'category':advert.bid.category.title,
                    'youtube_link': advert.youtube_link,
                }

    # Convert the dictionary to a list and sort by total views and likes
    ranked_creators = sorted(top_video_stats.values(), key=lambda x: x['total'], reverse=True)

    context = {
        'ranked_creators': ranked_creators,  # Add ranked creators to the context
    }

    return render(request, 'course/ranking_dashboard.html', context)


from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class LogoutView(BaseLogoutView):
    @method_decorator(csrf_exempt)  # Disable CSRF protection for this view (not recommended)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)