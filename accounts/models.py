from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    """
    1-to-1 extension of Django User model for Bolbash Beauty Spot salon customers.
    Stores customer contact information, default shipping/booking address, and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=30, blank=True, help_text="Primary phone / WhatsApp number.")
    address = models.TextField(blank=True, help_text="Default address for delivery/contact.")
    city = models.CharField(max_length=100, default='Ibadan')
    state = models.CharField(max_length=100, default='Oyo State')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"
        ordering = ['-created_at']

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{full_name or self.user.username} ({self.user.email})"

    def get_full_address(self):
        parts = [self.address, self.city, self.state]
        return ", ".join([p for p in parts if p])
