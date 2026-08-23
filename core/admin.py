from django.contrib import admin
from .models import GalleryImage, ContactSubmission, Review, CustomerFeedback


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'caption')
    list_editable = ('display_order', 'is_active')


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer_name', 'get_booking_reference', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'booking__reference', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_reviews', 'reject_reviews', 'set_pending_reviews']

    def get_customer_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_customer_name.short_description = 'Customer'

    def get_booking_reference(self, obj):
        return obj.booking.reference if obj.booking else 'N/A'
    get_booking_reference.short_description = 'Booking Ref'

    @admin.action(description="Approve selected customer reviews")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(status=Review.STATUS_APPROVED)
        self.message_user(request, f"{updated} review(s) successfully marked as Approved.")

    @admin.action(description="Reject selected customer reviews")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(status=Review.STATUS_REJECTED)
        self.message_user(request, f"{updated} review(s) successfully marked as Rejected.")

    @admin.action(description="Set selected customer reviews to Pending Moderation")
    def set_pending_reviews(self, request, queryset):
        updated = queryset.update(status=Review.STATUS_PENDING)
        self.message_user(request, f"{updated} review(s) set to Pending Moderation.")


@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'category', 'rating', 'status', 'created_at')
    list_filter = ('status', 'category', 'rating', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message', 'admin_notes')
    readonly_fields = ('created_at', 'updated_at')



