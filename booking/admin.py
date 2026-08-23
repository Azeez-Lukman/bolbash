from django.contrib import admin
from .models import ServiceCategory, Service, BusinessHours, BlockedDate, Booking


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('display_order', 'name')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'featured', 'active', 'display_order')
    list_filter = ('category', 'featured', 'active')
    search_fields = ('name', 'short_description', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'opening_time', 'closing_time', 'is_active')
    list_editable = ('opening_time', 'closing_time', 'is_active')
    ordering = ('day_of_week',)


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('reason',)
    ordering = ('date',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer_name', 'customer_phone', 'service_name_snapshot', 'appointment_date', 'appointment_time', 'status', 'payment_status', 'amount_due')
    list_filter = ('status', 'payment_status', 'appointment_date', 'service')
    search_fields = ('reference', 'customer_name', 'customer_phone', 'customer_email', 'service_name_snapshot')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    ordering = ('-appointment_date', '-appointment_time')
