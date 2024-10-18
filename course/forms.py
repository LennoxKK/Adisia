from django import forms
from accounts.models import User
from .models import Category, Bid, BidApplication, Upload, UploadVideo,Advert,BidAllocation
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .validators import validate_youtube_url


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})



class BidAddForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Store the user
        super().__init__(*args, **kwargs)

        # Update widget attributes
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["category"].widget.attrs.update({"class": "form-control"})
        self.fields["deadline"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        # Call the super save method to handle saving the bid
        bid = super().save(commit=False)
        
        # Automatically set the creator field if creating a new bid
        if not bid.pk:  # Only set for new instances
            bid.creator = self.user  # Set creator to the user stored in init

        if commit:
            bid.save()
        return bid




class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'youtube_link', 'bid']  # Excluding 'category'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super(AdvertForm, self).__init__(*args, **kwargs)

        # Filter bids to include only those allocated to the content creator
        if user and user.is_content_creator:
            allocated_bids = BidAllocation.objects.filter(content_creator=user).values_list('bid', flat=True)
            available_bids = Bid.objects.filter(id__in=allocated_bids)

            # If no bids are allocated, set a default choice
            if not available_bids.exists():
                self.fields['bid'].choices = [('', 'No bids allocated to you')]
            else:
                self.fields['bid'].queryset = available_bids
        else:
            # For other users, you can handle it differently if needed
            self.fields['bid'].queryset = Bid.objects.exclude(advert__isnull=False)

        # Add the validator for youtube_link
        self.fields['youtube_link'].validators.append(validate_youtube_url)

    def clean(self):
        cleaned_data = super().clean()
        bid = cleaned_data.get('bid')

        if bid:
            # Automatically set the category based on the selected bid
            cleaned_data['category'] = bid.category  # Assuming 'category' is a ForeignKey in the Bid model
        else:
            self.add_error('bid', 'You must select a bid.')

        return cleaned_data

    def save(self, commit=True):
        advert = super().save(commit=False)
        if 'category' in self.cleaned_data:
            advert.category = self.cleaned_data['category']  # Assuming 'category' is a field in Advert
        
        if commit:
            advert.save()

        return advert


class BidAllocationForm(forms.ModelForm):
    bid = forms.ModelChoiceField(
        queryset=Bid.objects.none(),  # Initialize with an empty queryset
        widget=forms.RadioSelect,  # Radio button for selecting one bid
        required=True,
    )
    content_creator = forms.ModelChoiceField(
        queryset=User.objects.filter(is_content_creator=True),  # Fetch all content creators
        widget=forms.Select(attrs={"class": "browser-default custom-select"}),
        label="Content Creator",
    )

    class Meta:
        model = BidApplication
        fields = ["content_creator", "bid"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")  # Extract the user from kwargs
        super(BidAllocationForm, self).__init__(*args, **kwargs)

        # Filter content creators who have applied for bids created by the current user
        self.fields["content_creator"].queryset = User.objects.filter(
            is_content_creator=True,
            id__in=BidApplication.objects.filter(
                bid__advertiser=user
            ).values_list('applicants', flat=True)
        ).exclude(
            id__in=BidApplication.objects.values_list('content_creator', flat=True)  # Exclude already allocated content creators
        )

        # Filter bids based on the current user's created bids
        if user:
            # Get bids created by the current user
            created_bids = Bid.objects.filter(advertiser=user)

            # Get bids that have already been allocated
            allocated_bids = BidApplication.objects.values_list('bid__id', flat=True)

            # Exclude already allocated bids
            self.fields['bid'].queryset = created_bids.exclude(id__in=allocated_bids).distinct()


class EditBidAllocationForm(forms.ModelForm):
    bids = forms.ModelMultipleChoiceField(
        queryset=Bid.objects.all().order_by("updated_date"),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    content_creator = forms.ModelChoiceField(
        queryset=User.objects.filter(is_content_creator=True)[:5],
        widget=forms.Select(attrs={"class": "browser-default custom-select"}),
        label="Content Creator",
    )

    class Meta:
        model = BidApplication
        fields = ["content_creator", "bids"]

    def __init__(self, *args, **kwargs):
        super(EditBidAllocationForm, self).__init__(*args, **kwargs)
        self.fields["content_creator"].queryset = User.objects.filter(is_content_creator=True)[:5]


# Upload files to specific bid
class UploadFormFile(forms.ModelForm):
    class Meta:
        model = Upload
        fields = (
            "title",
            "file",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["file"].widget.attrs.update({"class": "form-control"})


# Upload video to specific bid
class UploadFormVideo(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = (
            "title",
            "video",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["video"].widget.attrs.update({"class": "form-control"})


class BidApplicationForm(forms.ModelForm):
    class Meta:
        model = BidApplication
        fields = ['bid', 'applicants']  # Specify fields

        # Set HiddenInput widgets to hide fields in the form
        widgets = {
            'bid': forms.HiddenInput(),
            'applicants': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Extract 'user' and 'bid' from the passed arguments
        user = kwargs.pop('user', None)
        bid = kwargs.pop('bid', None)
        super().__init__(*args, **kwargs)

        # Ensure only the current user is added as the applicant (single user)
        if user:
            self.fields['applicants'].initial = [user]  # Set current user as the only applicant

        # Set the initial bid value from the provided bid
        if bid:
            self.fields['bid'].initial = bid

        # Hide the fields using HiddenInput widgets
        self.fields['applicants'].widget = forms.HiddenInput()
        self.fields['bid'].widget = forms.HiddenInput()

class BidUpdateForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['title', 'summary', 'category', 'deadline']  # Include the fields you want to update

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)
        if user and user.is_advertiser:
            self.fields['category'].queryset = Category.objects.filter(advertiser=user)