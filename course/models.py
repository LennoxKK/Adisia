from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save, post_save, post_delete
from django.db.models import Q
from django.dispatch import receiver
from .utils import unique_slug_generator
from core.models import ActivityLog
import string
import random
from django.utils import timezone

# Category Manager for searching categories
class CategoryManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = Q(title__icontains=query) | Q(summary__icontains=query)
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

# Category Model
class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    summary = models.TextField(null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    objects = CategoryManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"pk": self.pk})

@receiver(post_save, sender=Category)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The category '{instance}' has been {verb}.")

@receiver(post_delete, sender=Category)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The category '{instance}' has been deleted.")

# Bid Manager for searching bids
class BidManager(models.Manager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(code__icontains=query) |
                Q(slug__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

# Bid Model
class Bid(models.Model):
    slug = models.SlugField(blank=True, unique=True)
    title = models.CharField(max_length=200, null=True)
    code = models.CharField(max_length=10, unique=True, blank=True, editable=False)
    summary = models.TextField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_bids', null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    deadline = models.DateTimeField(null=True, blank=True)

    objects = BidManager()

    def __str__(self):
        return "{0} ({1})".format(self.title, self.code)

    def get_absolute_url(self):
        return reverse("bid_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.generate_code()
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)

    def generate_code(self):
        length = 6
        characters = string.ascii_uppercase + string.digits
        random_code = ''.join(random.choice(characters) for _ in range(length))
        return f"BID{random_code}"

@receiver(post_save, sender=Bid)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The bid '{instance}' has been {verb}.")

@receiver(post_delete, sender=Bid)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The bid '{instance}' has been deleted.")

# Bid Application Model
class BidApplication(models.Model):
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="applications",
        blank=True
    )
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="applied_bid", null=True)

    def __str__(self):
        return str(self.bid)

# Bid Allocation Model
class BidAllocation(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="allocations")
    content_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allocated_bids')
    application = models.ForeignKey(BidApplication, on_delete=models.CASCADE, related_name="allocations", null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('allocated', 'Allocated'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='allocated')
    allocated_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.bid.title} allocated to {self.content_creator.username}"
    def is_overdue(self):
        return self.completion_date < timezone.now()

@receiver(post_save, sender=BidAllocation)
def log_save(sender, instance, created, **kwargs):
    verb = "allocated" if created else "updated"
    ActivityLog.objects.create(message=f"The bid '{instance.bid.title}' has been {verb} to '{instance.content_creator.username}'.")

@receiver(post_delete, sender=BidAllocation)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The allocation of the bid '{instance.bid.title}' to '{instance.content_creator.username}' has been deleted.")

# Advert Model
class Advert(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True, blank=True)
    youtube_link = models.URLField(max_length=200, null=True, blank=True)
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name="advert")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='adverts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("advert_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)

@receiver(post_save, sender=Advert)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The advert '{instance.title}' has been {verb}.")

@receiver(post_delete, sender=Advert)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The advert '{instance.title}' has been deleted.")

# Upload Model for documents related to bids
class Upload(models.Model):
    title = models.CharField(max_length=100)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="bid_files/",
        help_text="Valid Files: pdf, docx, doc, xls, xlsx, ppt, pptx, zip, rar, 7zip",
        validators=[FileExtensionValidator(
            [
                "pdf",
                "docx",
                "doc",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "zip",
                "rar",
                "7zip",
            ]
        )],
    )
    updated_date = models.DateTimeField(auto_now=True, null=True)
    upload_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.file)[6:]

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

@receiver(post_save, sender=Upload)
def log_save(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            message=f"The file '{instance.title}' has been uploaded to the bid '{instance.bid}'."
        )
    else:
        ActivityLog.objects.create(
            message=f"The file '{instance.title}' of the bid '{instance.bid}' has been updated."
        )

@receiver(post_delete, sender=Upload)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        message=f"The file '{instance.title}' of the bid '{instance.bid}' has been deleted."
    )

# Upload Video Model for video uploads related to bids
class UploadVideo(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to="bid_videos/",
        help_text="Valid video formats: mp4, mkv, wmv, 3gp, f4v, avi, mp3",
        validators=[FileExtensionValidator(["mp4", "mkv", "wmv", "3gp", "f4v", "avi", "mp3"])]
    )
    summary = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse(
            "video_single", kwargs={"slug": self.bid.slug, "video_slug": self.slug}
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)

@receiver(post_save, sender=UploadVideo)
def log_save(sender, instance, created, **kwargs):
    verb = "created" if created else "updated"
    ActivityLog.objects.create(message=f"The video '{instance.title}' has been {verb}.")

@receiver(post_delete, sender=UploadVideo)
def log_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(message=f"The video '{instance.title}' has been deleted.")
