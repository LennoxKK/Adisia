from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django_filters.views import FilterView
from django.shortcuts import render, redirect
from accounts.models import User  # Assuming ContentCreator replaces Student
# from core.models import Session, Semester
# from result.models import TakenBid  # Assuming equivalent to TakenCourse
from accounts.decorators import advertiser_required, content_creator_required  # Adjusted decorators
from .forms import (
    CategoryForm,
    BidAddForm,
    BidAllocationForm,
    EditBidAllocationForm,
    UploadFormFile,
    UploadFormVideo,
    AdvertForm
)
from .filters import CategoryFilter, BidAllocationFilter
from .models import Category, Bid, BidAllocation, Upload, UploadVideo, BidApplication,Advert

from django.db import DatabaseError

# View for content creators to apply for a bid
@login_required
@content_creator_required
def apply_for_bid(request, code):
    bid = get_object_or_404(Bid, code=code)

    # Check if the user has already applied for this bid
    if BidApplication.objects.filter(applicants=request.user, bid=bid).exists():
        messages.warning(request, "You have already applied for this bid.")
        return redirect('home')

    if request.method == 'POST':
        try:
            bid_application, created = BidApplication.objects.get_or_create(bid=bid)
            bid_application.applicants.add(request.user)
            bid_application.save()

            if created:
                messages.success(request, "Your application has been successfully submitted.")
            else:
                messages.info(request, "You have been added to the existing application for this bid.")
            return redirect('home')
        except DatabaseError as db_error:
            messages.error(request, f"Database error: {str(db_error)}")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')

    context = {
        'bid': bid,
    }
    return render(request, 'bid/apply_for_bid.html', context)


@method_decorator([login_required], name="dispatch")
class CategoryFilterView(FilterView):
    filterset_class = CategoryFilter
    template_name = "course/category_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


@login_required
@advertiser_required
def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.success(
                    request, f"{form.cleaned_data['title']} category has been created."
                )
                return redirect("categories")
            else:
                # Handle form errors and display them as messages
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        except Exception as e:
            # Capture any exception and display as a message
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = CategoryForm()

    return render(
        request,
        "course/category_add.html",
        {
            "title": "Add Category",
            "form": form,
        },
    )




@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Check the user's role
    if request.user.is_content_creator:
        # Show only the bids that the content creator has applied for
        bids = Bid.objects.filter(applied_bid__applicants=request.user, category=category).order_by("-updated_date")
    elif request.user.is_advertiser:
        # Show only the bids that belong to the current advertiser
        bids = Bid.objects.filter(creator=request.user, category=category).order_by("-updated_date")
    elif request.user.is_superuser:
        # Show all bids in the category for super users
        bids = Bid.objects.filter(category=category).order_by("-updated_date")
    else:
        # If the user has neither role, you can handle accordingly
        bids = Bid.objects.none()  # No bids for other roles

    # Paginate bids, with 5 bids per page for superusers and all other users
    paginator = Paginator(bids, 5)
    page = request.GET.get("page")
    bids = paginator.get_page(page)

    return render(
        request,
        "course/category_single.html",
        {
            "title": category.title,
            "category": category,
            "bids": bids,
        },
    )




@login_required
@advertiser_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{form.cleaned_data['title']} category has been updated."
            )
            return redirect("categories")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "bid/category_add.html",
        {"title": "Edit Category", "form": form},
    )


@login_required
@advertiser_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    title = category.title
    category.delete()
    messages.success(request, f"Category {title} has been deleted.")

    return redirect("categories")


# ########################################################
# Bid views
# ########################################################
@login_required
def bid_single(request, slug):
    bid = get_object_or_404(Bid, slug=slug)
    files = Upload.objects.filter(bid=bid)
    videos = UploadVideo.objects.filter(bid=bid)
    assigned_creators = BidAllocation.objects.filter(bid=bid)

    if assigned_creators.exists():
        # If there are assigned content creators, display only them
        content_creators = assigned_creators
    else:
        # If no creators are assigned, get all applicants for the current bid
        all_applicants = BidApplication.objects.filter(bid=bid).values_list('applicants', flat=True)

        # Get content creators who have allocations in other bids
        allocated_creators = BidAllocation.objects.exclude(bid=bid).values_list('content_creator', flat=True)

        # Filter out those who have been allocated to other bids
        content_creators = all_applicants.exclude(id__in=allocated_creators)

    return render(
        request,
        "course/bid_single.html",
        {
            "title": bid.title,
            "bid": bid,
            "files": files,
            "videos": videos,
            "content_creators": content_creators,
            "media_url": settings.MEDIA_URL,
        },
    )


@login_required
@advertiser_required
def bid_add(request, pk):
    try:
        if request.method == "POST":
            form = BidAddForm(request.POST, user=request.user)
            if form.is_valid():
                bid = form.save(commit=False)
                bid.creator = request.user  # Set the advertiser (creator of the bid)
                bid.save()
                messages.success(
                    request, f"{bid.title} ({bid.code}) has been created."
                )
                return redirect("category_detail", pk=request.POST.get("category"))
            else:
                # Handle form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
        else:
            # Initial form with pre-filled category
            form = BidAddForm(
                initial={"category": Category.objects.get(pk=pk)}, user=request.user
            )
    except Category.DoesNotExist:
        messages.error(request, "The specified category does not exist.")
        return redirect("categories")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(
        request,
        "bid/bid_add.html",
        {
            "title": "Add Bid",
            "form": form,
            "category": pk,
        },
    )


@login_required
@advertiser_required
def bid_edit(request, slug):
    bid = get_object_or_404(Bid, slug=slug)
    if request.method == "POST":
        form = BidAddForm(request.POST, instance=bid)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{bid.title} ({bid.code}) has been updated."
            )
            return redirect("category_detail", pk=request.POST.get("category"))
        else:
            messages.error(request, "Correct the error(s) below.")
    else:
        form = BidAddForm(instance=bid)

    return render(
        request,
        "bid/bid_add.html",
        {
            "title": "Edit Bid",
            "form": form,
        },
    )


@login_required
@advertiser_required
def bid_delete(request, slug):
    bid = get_object_or_404(Bid, slug=slug)
    bid_title = bid.title
    bid.delete()
    messages.success(request, f"Bid {bid_title} has been deleted.")

    return redirect("category_detail", pk=bid.category.id)


# ########################################################
# Bid Allocation
# ########################################################
@method_decorator([login_required], name="dispatch")
class BidAllocationFormView(CreateView):
    form_class = BidAllocationForm
    template_name = "bid/bid_allocation_form.html"

    def get_form_kwargs(self):
        kwargs = super(BidAllocationFormView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        content_creator = form.cleaned_data["content_creator"]
        selected_bid = form.cleaned_data["bid"]

        # Check if a BidAllocation exists for the content creator and bid
        allocation, created = BidAllocation.objects.get_or_create(
            content_creator=content_creator,
            bid=selected_bid
        )

        if created:
            messages.success(
                self.request, f"Bid {selected_bid} has been allocated to {content_creator}."
            )
        else:
            messages.info(
                self.request, f"{content_creator} is already allocated to {selected_bid}."
            )

        return redirect("bid_allocation_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Assign Bid"
        return context


@method_decorator([login_required], name="dispatch")
class BidAllocationFilterView(FilterView):
    filterset_class = BidAllocationFilter
    template_name = "bid/bid_allocation_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Bid Allocations"
        return context


@login_required
@advertiser_required
def edit_allocated_bid(request, pk):
    allocation = get_object_or_404(BidAllocation, pk=pk)
    if request.method == "POST":
        form = EditBidAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, "Bid allocation has been updated.")
            return redirect("bid_allocation_view")
    else:
        form = EditBidAllocationForm(instance=allocation)

    return render(
        request,
        "bid/bid_allocation_form.html",
        {"title": "Edit Bid Allocation", "form": form},
    )


@login_required
@advertiser_required
def deallocate_bid(request, pk):
    allocation = get_object_or_404(BidAllocation, pk=pk)
    allocation.delete()
    messages.success(request, "Successfully deallocated bid.")
    return redirect("bid_allocation_view")


# ########################################################
# File Upload views
# ########################################################
@login_required
@advertiser_required
def handle_file_upload(request, slug):
    bid = get_object_or_404(Bid, slug=slug)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.bid = bid
            obj.save()
            messages.success(
                request, f"{obj.title} has been uploaded."
            )
            return redirect("bid_detail", slug=slug)
    else:
        form = UploadFormFile()
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "File Upload", "form": form, "bid": bid},
    )


@login_required
@advertiser_required
def handle_file_edit(request, slug, file_id):
    bid = get_object_or_404(Bid, slug=slug)
    instance = get_object_or_404(Upload, pk=file_id)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{instance.title} has been updated."
            )
            return redirect("bid_detail", slug=slug)
    else:
        form = UploadFormFile(instance=instance)

    return render(
        request,
        "upload/upload_file_form.html",
        {"title": instance.title, "form": form, "bid": bid},
    )


@login_required
@advertiser_required
def handle_file_delete(request, slug, file_id):
    file = get_object_or_404(Upload, pk=file_id)
    file_title = file.title
    file.delete()

    messages.success(request, f"{file_title} has been deleted.")
    return redirect("bid_detail", slug=slug)


# ########################################################
# Video Upload views
# ########################################################
@login_required
@advertiser_required
def handle_video_upload(request, slug):
    bid = get_object_or_404(Bid, slug=slug)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.bid = bid
            obj.save()
            messages.success(
                request, f"{obj.title} has been uploaded."
            )
            return redirect("bid_detail", slug=slug)
    else:
        form = UploadFormVideo()
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Video Upload", "form": form, "bid": bid},
    )


@login_required
def handle_video_single(request, slug, video_slug):
    bid = get_object_or_404(Bid, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(request, "upload/video_single.html", {"video": video})


@login_required
@advertiser_required
def handle_video_edit(request, slug, video_slug):
    bid = get_object_or_404(Bid, slug=slug)
    instance = get_object_or_404(UploadVideo, slug=video_slug)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"{instance.title} has been updated."
            )
            return redirect("bid_detail", slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(
        request,
        "upload/upload_video_form.html",
        {"title": instance.title, "form": form, "bid": bid},
    )


@login_required
@advertiser_required
def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    video_title = video.title
    video.delete()

    messages.success(request, f"{video_title} has been deleted.")
    return redirect("bid_detail", slug=slug)


# ########################################################
# Bid Registration
# ########################################################
@login_required
@content_creator_required
def bid_registration(request):
    if request.method == "POST":
        content_creator = get_object_or_404(ContentCreator, user=request.user)
        selected_bids = request.POST.getlist('bid_ids')
        for bid_id in selected_bids:
            bid = get_object_or_404(Bid, pk=bid_id)
            TakenBid.objects.create(content_creator=content_creator, bid=bid)
        messages.success(request, "Bids registered successfully!")
        return redirect("bid_registration")
    else:
        content_creator = get_object_or_404(ContentCreator, user=request.user)
        taken_bids = TakenBid.objects.filter(content_creator=content_creator)
        registered_bid_ids = taken_bids.values_list('bid__id', flat=True)

        available_bids = Bid.objects.exclude(id__in=registered_bid_ids)
        context = {
            "available_bids": available_bids,
            "taken_bids": taken_bids,
            "content_creator": content_creator,
        }
        return render(request, "bid/bid_registration.html", context)


@login_required
@content_creator_required
def bid_drop(request):
    if request.method == "POST":
        content_creator = get_object_or_404(ContentCreator, user=request.user)
        selected_bids = request.POST.getlist('bid_ids')
        for bid_id in selected_bids:
            bid = get_object_or_404(Bid, pk=bid_id)
            taken_bid = get_object_or_404(TakenBid, content_creator=content_creator, bid=bid)
            taken_bid.delete()
        messages.success(request, "Bids dropped successfully!")
        return redirect("bid_registration")


# ########################################################



@login_required
def user_bid_list(request):
    try:
        if request.user.is_advertiser:
            # Fetch bids created by the advertiser
            bids = Bid.objects.filter(creator=request.user)
            print(bids)
            if not bids.exists():
                messages.info(request, "You have not created any bids.")
            return render(request, "course/user_bid_list.html", {"bids": bids})

        elif request.user.is_content_creator:
            # Use request.user directly as the content creator
            content_creator = request.user
            # Fetch bids allocated to the content creator
            bids_applied_for = BidApplication.objects.filter(applicants=content_creator).values_list('bid', flat=True)

            # Get the actual Bid objects
            bids = Bid.objects.filter(id__in=bids_applied_for)
            if not bids.exists():
                messages.info(request, "You have not applied for any bids.")
            return render(
                request,
                "course/user_bid_list.html",
                {"content_creator": content_creator, "bids": bids},
            )

        else:
            messages.warning(request, "You do not have access to any bids.")
            return render(request, "course/user_bid_list.html", {"bids": []})

    except Exception as e:
        # Capture any unexpected errors and display them as a message
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, "course/user_bid_list.html", {"bids": []})


@login_required
@content_creator_required
def add_advert(request):
    # Check if the user has any allocated bids
    allocated_bids = BidAllocation.objects.filter(content_creator=request.user, status='allocated')

    if not allocated_bids.exists():
        messages.error(request, "You must be allocated at least one bid to create an advert.")
        return redirect('content_creator_workspace')  # Redirect if no allocated bids

    if request.method == 'POST':
        form = AdvertForm(request.POST, user=request.user)  # Pass user here
        try:
            if form.is_valid():
                advert = form.save(commit=False)
                advert.creator = request.user  # Set the creator as the logged-in user
                advert.save()
                messages.success(request, 'Advert created successfully!')
                return redirect('content_creator_workspace')  # Redirect to the adverts list page
            else:
                error_messages = ', '.join([f"{field.label}: {', '.join(errors)}" for field, errors in form.errors.items()])
                messages.error(request, f"Please correct the following errors: {error_messages}")
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = AdvertForm(user=request.user)  # Pass user here

    return render(request, 'course/add_advert.html', {'form': form})


@login_required
def advert_detail(request, slug):
    try:
        advert = get_object_or_404(Advert, slug=slug)  # Retrieve the advert by slug
        return render(request, 'course/advert_detail.html', {'advert': advert})  # Render the detail page with the advert
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")
        return render(request, 'course/advert_detail.html', {'advert': None})  # Optionally render with no advert on error



@login_required
def edit_advert(request, slug):
    advert = get_object_or_404(Advert, slug=slug)  # Retrieve the advert by slug

    if request.method == 'POST':
        form = AdvertForm(request.POST, instance=advert)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Advert updated successfully!')
                return redirect('advert_detail', slug=advert.slug)  # Redirect to the advert detail page
            else:
                # Capture specific form errors
                error_messages = form.errors.as_text()
                messages.error(request, f"Please fix the following errors:\n{error_messages}")
        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = AdvertForm(instance=advert)  # Populate form with existing advert data

    return render(request, 'course/edit_advert.html', {'form': form, 'advert': advert})
@login_required
def delete_advert(request, slug):
    advert = get_object_or_404(Advert, slug=slug)  # Retrieve the advert by slug

    if request.method == 'POST':
        try:
            advert.delete()  # Delete the advert
            messages.success(request, 'Advert deleted successfully!')
            return redirect('advert_list')  # Redirect to the adverts list page
        except Exception as e:
            messages.error(request, f"An unexpected error occurred while deleting the advert: {e}")

    return render(request, 'course/delete_advert.html', {'advert': advert})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden,HttpResponse
from .models import Bid, BidApplication, BidAllocation, Advert
from django.core.mail import send_mail
from django.template.loader import render_to_string
from accounts.utils import EmailThread






@login_required
def allocate_bid(request, bid_slug):
    # Get the bid by slug
    bid = get_object_or_404(Bid, slug=bid_slug)

    # Ensure only the creator (advertiser) or admin can allocate/deallocate the bid
    if request.user != bid.creator and not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to allocate or deallocate this bid.")

    # Check if the bid has already been allocated
    allocation = BidAllocation.objects.filter(bid=bid, status='allocated').first()

    # Handle bid deallocation
    if allocation and request.method == 'POST':
        # Check if the current date is past the completion date
        if timezone.now().date() >= allocation.completion_date:
            # Deallocate the bid
            allocation.status = 'deallocated'
            allocation.save()
            messages.success(request, "Bid deallocated successfully.")
            return redirect('bid_detail', slug=bid.slug)
        else:
            messages.warning(request, "You cannot deallocate the bid yet. The completion date has not been reached.")

    # Prevent reallocation if already allocated
    if allocation:
        messages.warning(request, "This bid has already been allocated. Deallocate first to reallocate.")
        return redirect('bid_detail', slug=bid.slug)

    # Get all applicants for the bid
    applicants = BidApplication.objects.filter(bid=bid).values_list('applicants', flat=True)

    # Filter content creators based on the applicants
    content_creators = User.objects.filter(id__in=applicants)

    # Determine the top 3 creators based on total views and likes from their adverts
    top_3_creators = (
        content_creators.annotate(
            total_views=Sum('adverts__views'),  # Use 'adverts__views'
            total_likes=Sum('adverts__likes')   # Use 'adverts__likes'
        )
        .order_by('-total_views', '-total_likes')[:3]
    )

    if request.method == 'POST':
        # Check for completion date from the form
        completion_date = request.POST.get('completion_date')
        if completion_date:
            # Finalize the allocation with the completion date
            for creator in top_3_creators:
                BidAllocation.objects.create(
                    bid=bid,
                    content_creator=creator,
                    status='allocated',
                    completion_date=completion_date
                )
                # Send email to the allocated content creator
                send_bid_allocation_email(creator, bid)

            # Show success message
            messages.success(request, "Bid allocated successfully.")
            return redirect('bid_detail', slug=bid.slug)
        else:
            messages.error(request, "Please provide a completion date.")

    # Render the completion date form or the allocation view
    return render(request, 'course/add_completion_date.html', {
        'bid': bid,
        'allocation': allocation,  # Pass allocation object to the template
        'top_3_creators': top_3_creators,  # Pass top creators to the template if needed
    })

def send_bid_allocation_email(content_creator, bid):
    """
    Function to send an email to content creators allocated to a bid.
    """
    template_name = "accounts/email/bid_allocation_notification.html"
    email = {
        "subject": "Congratulations! You've been allocated a new bid",
        "recipient_list": [content_creator.email],
        "template_name": template_name,
        "context": {
            "user": content_creator,
            "bid": bid,
        },
    }
    EmailThread(**email).start()

