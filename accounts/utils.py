from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings
import threading
from core.utils import send_html_email


from django.contrib.auth import get_user_model

def generate_password(length=8, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'):
    """
    Generate a random password for the user.

    Args:
        length (int): Length of the password. Default is 8.
        allowed_chars (str): Characters allowed in the password. Default includes letters, digits, and special characters.

    Returns:
        str: A randomly generated password.
    """
    return get_user_model().objects.make_random_password(length=length, allowed_chars=allowed_chars)



def generate_content_creator_id():
    # Generate a unique ID based on the current year and the number of content creators
    registered_year = datetime.now().strftime("%Y")
    creators_count = get_user_model().objects.filter(is_content_creator=True).count()
    return f"{settings.CONTENT_CREATOR_ID_PREFIX}-{registered_year}-{creators_count}"


def generate_advertiser_id():
    # Generate a unique ID based on the current year and the number of advertisers
    registered_year = datetime.now().strftime("%Y")
    advertisers_count = get_user_model().objects.filter(is_advertiser=True).count()
    return f"{settings.ADVERTISER_ID_PREFIX}-{registered_year}-{advertisers_count}"


def generate_content_creator_credentials():
    return generate_content_creator_id(), generate_password()


def generate_advertiser_credentials():
    return generate_advertiser_id(), generate_password()


class EmailThread(threading.Thread):
    def __init__(self, subject, recipient_list, template_name, context):
        self.subject = subject
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        send_html_email(
            subject=self.subject,
            recipient_list=self.recipient_list,
            template=self.template_name,
            context=self.context,
        )


def send_new_account_email(user, password):
    if user.is_content_creator:
        template_name = "accounts/email/new_content_creator_account_confirmation.html"
    else:
        template_name = "accounts/email/new_advertiser_account_confirmation.html"
    
    email = {
        "subject": "Your Adisia account confirmation and credentials",
        "recipient_list": [user.email],
        "template_name": template_name,
        "context": {"user": user, "password": password},
    }
    print(user,password)
    EmailThread(**email).start()
