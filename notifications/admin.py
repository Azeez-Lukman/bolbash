from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('booking', 'notification_type', 'recipient_email', 'status', 'sent_at')
    list_filter = ('status', 'notification_type', 'sent_at')
    search_fields = ('recipient_email', 'booking__reference', 'booking__customer_name', 'error_message')
    readonly_fields = ('booking', 'notification_type', 'recipient_email', 'status', 'error_message', 'sent_at')
    ordering = ('-sent_at',)
