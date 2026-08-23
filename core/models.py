from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from booking.models import ServiceCategory, Service, Booking


class GalleryImage(models.Model):
    """
    Model representing portfolio gallery items showcasing salon craftsmanship,
    bridal transformations, wig installations, natural hair, and events.
    """
    CATEGORY_CHOICES = [
        ('BRIDAL', 'Bridal & Wedding'),
        ('HAIRSTYLES', 'Hair Styling & Updos'),
        ('WIG_MELT', 'Wig Installation & Lace Melt'),
        ('TRANSFORMATION', 'Hair Transformation'),
        ('NATURAL_HAIR', 'Natural Hair & Maintenance'),
        ('EVENTS', 'Events & Special Occasions'),
    ]

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='HAIRSTYLES')
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_images')
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255, blank=True, help_text="Short description or client testimonial excerpt.")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text="Whether this image is visible on the public gallery page.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class ContactSubmission(models.Model):
    """
    Model storing customer contact form enquiries submitted from the public Contact page.
    Integrates into the Administration Panel for staff tracking and responses.
    """
    STATUS_NEW = 'NEW'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_RESPONDED = 'RESPONDED'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New Enquiry'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESPONDED, 'Responded'),
        (STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Enquiry"
        verbose_name_plural = "Customer Enquiries"

    def __str__(self):
        return f"Enquiry from {self.name} - {self.subject} ({self.get_status_display()})"


class Review(models.Model):
    """
    Model representing customer reviews and ratings for salon services and completed appointments.
    Provides moderation status architecture (Pending, Approved, Rejected) and duplicate prevention.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Moderation'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', help_text="Authenticated customer submitting the review.")
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='review',
        help_text="Optional completed salon appointment associated with this review."
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        help_text="Optional salon service associated with this review."
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 (poor) to 5 (excellent)."
    )
    comment = models.TextField(help_text="Customer review text and feedback.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, help_text="Moderation status.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"

    def __str__(self):
        customer = self.user.get_full_name() or self.user.username
        return f"Review ({self.rating}★) by {customer} - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.rating is not None:
            if self.rating < 1 or self.rating > 5:
                raise ValidationError({'rating': "Rating must be between 1 and 5 stars."})
        if self.comment:
            stripped = self.comment.strip()
            if not stripped:
                raise ValidationError({'comment': "Review comment cannot be empty or blank whitespace."})
            if len(stripped) > 2000:
                raise ValidationError({'comment': "Review comment cannot exceed 2000 characters."})
        elif not self.comment:
            raise ValidationError({'comment': "Review comment is required."})


class CustomerFeedback(models.Model):
    """
    Model storing customer feedback, suggestions, and complaints for salon services,
    academy training, or online shop products with staff resolution tracking.
    """
    CATEGORY_SALON = 'SALON'
    CATEGORY_ACADEMY = 'ACADEMY'
    CATEGORY_SHOP = 'SHOP'
    CATEGORY_GENERAL = 'GENERAL'

    CATEGORY_CHOICES = [
        (CATEGORY_SALON, 'Salon Experience'),
        (CATEGORY_ACADEMY, 'Beauty Academy'),
        (CATEGORY_SHOP, 'Product & Online Shop'),
        (CATEGORY_GENERAL, 'General Suggestion / Feedback'),
    ]

    STATUS_NEW = 'NEW'
    STATUS_IN_REVIEW = 'IN_REVIEW'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New Feedback'),
        (STATUS_IN_REVIEW, 'Under Staff Review'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks', help_text="Optional authenticated user.")
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Optional rating from 1 to 5 stars."
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_notes = models.TextField(blank=True, help_text="Internal staff notes and resolution details.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Feedback"
        verbose_name_plural = "Customer Feedbacks"

    def __str__(self):
        return f"Feedback from {self.name} [{self.get_category_display()}] - {self.get_status_display()}"


