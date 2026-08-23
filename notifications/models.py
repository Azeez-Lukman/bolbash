from django.db import models
from booking.models import Booking
from shop.models import Order
from academy.models import Enrollment, Certificate


class NotificationLog(models.Model):
    """
    Logs customer notifications dispatched across Email and WhatsApp channels.
    Prevents duplicate notifications, enforces idempotency, and records delivery status.
    """
    CHANNEL_EMAIL = 'EMAIL'
    CHANNEL_WHATSAPP = 'WHATSAPP'

    CHANNEL_CHOICES = (
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_WHATSAPP, 'WhatsApp'),
    )

    TYPE_BOOKING_CONFIRMATION = 'BOOKING_CONFIRMATION'
    TYPE_APPOINTMENT_REMINDER = 'APPOINTMENT_REMINDER'
    TYPE_APPOINTMENT_CANCELLATION = 'APPOINTMENT_CANCELLATION'
    TYPE_APPOINTMENT_RESCHEDULED = 'APPOINTMENT_RESCHEDULED'
    TYPE_ACADEMY_ENROLMENT = 'ACADEMY_ENROLMENT'
    TYPE_COURSE_COMPLETION = 'COURSE_COMPLETION'
    TYPE_ORDER_CONFIRMATION = 'ORDER_CONFIRMATION'
    TYPE_POST_APPOINTMENT_REVIEW = 'POST_APPOINTMENT_REVIEW'

    TYPE_CHOICES = (
        (TYPE_BOOKING_CONFIRMATION, 'Booking Confirmation'),
        (TYPE_APPOINTMENT_REMINDER, 'Appointment Reminder'),
        (TYPE_APPOINTMENT_CANCELLATION, 'Appointment Cancellation'),
        (TYPE_APPOINTMENT_RESCHEDULED, 'Appointment Rescheduled'),
        (TYPE_ACADEMY_ENROLMENT, 'Academy Enrolment'),
        (TYPE_COURSE_COMPLETION, 'Course Completion'),
        (TYPE_ORDER_CONFIRMATION, 'Order Confirmation'),
        (TYPE_POST_APPOINTMENT_REVIEW, 'Post-Appointment Review Request'),
    )

    STATUS_SENT = 'SENT'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = (
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    )

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    recipient = models.CharField(max_length=255, default='', blank=True, help_text="Email address or phone number of recipient.")
    recipient_email = models.EmailField(blank=True, null=True)

    # Optional Foreign Keys to Target Business Objects
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    subject_or_summary = models.CharField(max_length=255, blank=True, help_text="Subject line or summary snippet.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"

    def __str__(self):
        return f"[{self.get_channel_display()}] {self.get_notification_type_display()} to {self.recipient} ({self.status})"

