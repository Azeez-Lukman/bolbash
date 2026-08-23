from django.core.management.base import BaseCommand
from booking.models import Booking
from notifications.models import NotificationLog
from notifications.services import NotificationDispatcher


class Command(BaseCommand):
    help = "Dispatches post-appointment review request notifications via Email and WhatsApp to customers with completed salon appointments lacking prior review requests."

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='',
            help='Optional domain prefix for review link generation (e.g. https://bolbash.com).'
        )

    def handle(self, *args, **options):
        domain = options['domain']
        self.stdout.write("Searching for completed appointments requiring review requests...")

        # Find completed bookings without a successful POST_APPOINTMENT_REVIEW log
        already_sent_booking_ids = NotificationLog.objects.filter(
            notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW,
            status=NotificationLog.STATUS_SENT
        ).values_list('booking_id', flat=True)

        completed_bookings = Booking.objects.filter(
            status=Booking.STATUS_COMPLETED
        ).exclude(id__in=already_sent_booking_ids)

        total_count = completed_bookings.count()
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("No pending post-appointment review requests found."))
            return

        sent_count = 0
        for booking in completed_bookings:
            res = NotificationDispatcher.send_post_appointment_review_request(booking, domain=domain)
            if isinstance(res, dict) and (res.get('email') or res.get('whatsapp')):
                sent_count += 1
                self.stdout.write(f"  [OK] Review request dispatched for Booking #{booking.reference} ({booking.customer_name})")
            elif isinstance(res, tuple) and res[0]:
                sent_count += 1
                self.stdout.write(f"  [OK] Review request processed for Booking #{booking.reference} ({booking.customer_name})")
            else:
                self.stdout.write(f"  [SKIPPED/FAILED] Booking #{booking.reference} skipped or failed.")

        self.stdout.write(
            self.style.SUCCESS(f"Processed {total_count} completed appointments. Successfully dispatched {sent_count} review requests.")
        )
