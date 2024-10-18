from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.db import transaction
from .models import User,GENDERS
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User  # Ensure you import your User model
from django.core.exceptions import ValidationError



class ContentCreatorAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Username",
        required=True,  # Changed to True
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="First Name",
        required=True,  # Changed to True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Last Name",
        required=True,  # Changed to True
    )
    phone = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Mobile No.",
        required=True,  # Changed to True
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Email Address",
        required=True,  # Changed to True
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password",
        required=True,  # Changed to True
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password Confirmation",
        required=True,  # Changed to True
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Gender",
        required=True,  # Changed to True
    )
    picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email', 'password1', 'password2', 'gender', 'picture']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_content_creator = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        user.gender = self.cleaned_data.get("gender")
        user.picture = self.cleaned_data.get("picture")

        if commit:
            user.save()

        return user

class AdvertiserAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Username",
        required=False,
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="First Name",
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Last Name",
    )
    phone = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Mobile No.",
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Email Address",
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password",
        required=False,
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Password Confirmation",
        required=False,
    )
    picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_advertiser = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        user.picture = self.cleaned_data.get("picture")

        if commit:
            user.save()

        return user


class ProfileUpdateForm(UserChangeForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Email Address",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="First Name",
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Last Name",
    )
    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Gender",
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Phone No.",
    )
    picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone",
            "picture",
        ]


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address."
            self.add_error("email", msg)
            return email
