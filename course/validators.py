from django.core.exceptions import ValidationError
import re

def validate_youtube_url(value):
    youtube_regex = (
        r'^(https?://)?(www\.)?'
        '(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)'
        '[\w-]{10,12}$'
    )
    if not re.match(youtube_regex, value):
        raise ValidationError('Invalid YouTube URL. Please enter a valid URL.')
