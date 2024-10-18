from .utils import (
    generate_content_creator_credentials,
    generate_advertiser_credentials,
    send_new_account_email,
)

def post_save_account_receiver(sender, instance=None, created=False, *args, **kwargs):
    """
    Send email notification for new content creators and advertisers
    """
    if created:
        if instance.is_content_creator:
            username, password = generate_content_creator_credentials()
            instance.username = username
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_account_email(instance, password)

        if instance.is_advertiser:
            username, password = generate_advertiser_credentials()
            instance.username = username
            instance.set_password(password)
            instance.save()
            # Send email with the generated credentials
            send_new_account_email(instance, password)
