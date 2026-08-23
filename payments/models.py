import random, string
from django.db import models
from django.utils import timezone
from booking.models import Booking


class Payment(models.Model):
    """
    Stores payment transactions initialized and processed via Paystack.
    """
    STATUS_UNPAID = 'UNPAID'
    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_FAILED = 'FAILED'
    STATUS_REFUNDED = 'REFUNDED'

    STATUS_CHOICES = (
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    )

    PAYMENT_TYPE_BOOKING = 'BOOKING'
    PAYMENT_TYPE_COURSE = 'COURSE'
    PAYMENT_TYPE_ORDER = 'ORDER'

    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_BOOKING, 'Booking Deposit'),
        (PAYMENT_TYPE_COURSE, 'Course Tuition'),
        (PAYMENT_TYPE_ORDER, 'Shop Order'),
    )

    reference = models.CharField(max_length=50, unique=True, db_index=True, help_text="Internal unique payment reference e.g. BBS-PAY-XXXXXXXX")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    enrollment = models.ForeignKey('academy.Enrollment', on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    order = models.ForeignKey('shop.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_TYPE_BOOKING)

    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in NGN")
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    
    # Paystack Gateway Metadata
    paystack_reference = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    gateway_response = models.TextField(blank=True, null=True)
    channel = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. card, bank, ussd, transfer")
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - ₦{self.amount} ({self.get_status_display()})"

    @staticmethod
    def generate_reference():
        """Generates a human-readable unique payment reference format: BBS-PAY-XXXXXXXX"""
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"BBS-PAY-{suffix}"

    def save(self, *args, **kwargs):
        if not self.reference:
            ref = self.generate_reference()
            while Payment.objects.filter(reference=ref).exists():
                ref = self.generate_reference()
            self.reference = ref
        super().save(*args, **kwargs)
