from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('get_customer_name', 'get_email', 'phone_number', 'city', 'state', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone_number', 'city')
    list_filter = ('city', 'state', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_customer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_customer_name.short_description = 'Customer Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email Address'
