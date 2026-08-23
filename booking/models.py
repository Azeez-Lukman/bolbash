import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class ServiceCategory(models.Model):
    """
    Categorizes beauty services (e.g. Hair Styling, Wig Services, Nail & Beauty Care, Hair Treatment, Piercing).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    """
    Represents an individual salon/beauty service offered by Bolbash Beauty Spot.
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    short_description = models.CharField(max_length=255, help_text="Brief summary for cards and lists.")
    description = models.TextField(help_text="Detailed service description.")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in NGN. Leave empty if price is available on enquiry.")
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated duration in minutes.")
    featured = models.BooleanField(default=False, help_text="Highlight on homepage and top of services list.")
    active = models.BooleanField(default=True, help_text="Whether this service is available for viewing/booking.")
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:service_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BusinessHours(models.Model):
    """
    Defines salon operating hours for each day of the week.
    0 = Monday, 6 = Sunday.
    """
    DAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    day_of_week = models.IntegerField(choices=DAYS, unique=True)
    opening_time = models.TimeField(default='09:00:00')
    closing_time = models.TimeField(default='18:00:00')
    is_active = models.BooleanField(default=True, help_text="Whether the salon is open on this day.")

    class Meta:
        verbose_name = "Business Hours"
        verbose_name_plural = "Business Hours"
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.opening_time.strftime('%I:%M %p')} - {self.closing_time.strftime('%I:%M %p')}"


class BlockedDate(models.Model):
    """
    Represents specific calendar dates blocked from appointment booking (e.g. holidays, salon maintenance).
    """
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=255, blank=True, help_text="Reason for blocking this date.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Blocked: {self.date} ({self.reason or 'No reason provided'})"


class Booking(models.Model):
    """
    Stores individual appointment reservations created by customers.
    Preserves service price & duration snapshots at time of booking creation.
    """
    STATUS_PENDING_PAYMENT = 'PENDING_PAYMENT'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING_PAYMENT, 'Pending Payment'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    PAYMENT_UNPAID = 'UNPAID'
    PAYMENT_PENDING = 'PENDING'
    PAYMENT_PAID = 'PAID'
    PAYMENT_FAILED = 'FAILED'
    PAYMENT_REFUNDED = 'REFUNDED'

    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_UNPAID, 'Unpaid'),
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
        (PAYMENT_REFUNDED, 'Refunded'),
    )

    reference = models.CharField(max_length=30, unique=True, db_index=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Customer Details
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30)
    customer_email = models.EmailField()
    customer_note = models.TextField(blank=True)

    # Appointment Time Schedule
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)

    # Historical Snapshots
    service_name_snapshot = models.CharField(max_length=150)
    service_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_duration_snapshot = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes at booking time.")

    # Status & Payment Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_PAYMENT)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"{self.reference} - {self.customer_name} ({self.service_name_snapshot})"

    @staticmethod
    def generate_reference():
        """Generates a human-readable unique reference format: BBS-YYYYMMDD-XXXX"""
        from django.utils import timezone
        import random, string
        date_str = timezone.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"BBS-{date_str}-{random_suffix}"

    def save(self, *args, **kwargs):
        if not self.reference:
            ref = self.generate_reference()
            while Booking.objects.filter(reference=ref).exists():
                ref = self.generate_reference()
            self.reference = ref
        super().save(*args, **kwargs)
