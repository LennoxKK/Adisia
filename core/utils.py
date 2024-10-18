from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.template import TemplateDoesNotExist


def send_email(user, subject, msg):
    """Send a plain text email."""
    send_mail(
        subject,
        msg,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
    )


def send_html_email(subject, recipient_list, template, context):
    """A function responsible for sending HTML email."""
    try:
        # Render the HTML template
        html_message = render_to_string(template, context)
        
        # Generate plain text version of the email
        plain_message = strip_tags(html_message)

        # Send the email
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_FROM_ADDRESS,
            recipient_list,
            html_message=html_message,
            fail_silently=False,  # Optionally set to True if you want to suppress errors
        )
        
    except TemplateDoesNotExist:
        print(f"Template '{template}' does not exist.")
        # Optionally handle fallback or log the error
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        # You can also log the error or handle it as needed
