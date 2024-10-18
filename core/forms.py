# from django import forms
# from django.db import transaction

# # Assuming these models exist
# from .models import NewsAndEvents  # Adjust as necessary for your app's structure

# class YouTubeLinkForm(forms.Form):
#     youtube_link = forms.URLField(
#         label='YouTube Video Link', 
#         required=True, 
#         widget=forms.URLInput(attrs={'placeholder': 'Enter YouTube video URL', 'class': 'form-control'})
#     )

# # News and Events
# class NewsAndEventsForm(forms.ModelForm):
#     class Meta:
#         model = NewsAndEvents
#         fields = ("title", "summary", "posted_as")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["title"].widget.attrs.update({"class": "form-control"})
#         self.fields["summary"].widget.attrs.update({"class": "form-control"})
#         self.fields["posted_as"].widget.attrs.update({"class": "form-control"})


# # Session form (if needed in the future)
# class SessionForm(forms.Form):  # Adjust if there is a model for Session
#     session_name = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Session Name"}),
#         label="Session Name"
#     )
#     is_current_session = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
#         label="Is Current Session?"
#     )
#     next_session_begins = forms.DateTimeField(
#         widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#         required=True,
#         label="Next Session Begins"
#     )


# # Semester form (if needed in the future)
# class SemesterForm(forms.Form):  # Adjust if there is a model for Semester
#     semester_name = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Semester Name"}),
#         label="Semester"
#     )
#     is_current_semester = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
#         label="Is Current Semester?"
#     )
#     next_semester_begins = forms.DateTimeField(
#         widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#         required=True,
#         label="Next Semester Begins"
#     )
