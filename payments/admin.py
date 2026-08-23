from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'booking', 'amount', 'currency', 'status', 'paystack_reference', 'paid_at', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('reference', 'paystack_reference', 'booking__reference', 'booking__customer_name', 'booking__customer_email')
    readonly_fields = ('reference', 'paystack_reference', 'gateway_response', 'paid_at', 'created_at', 'updated_at')
    ordering = ('-created_at',)
