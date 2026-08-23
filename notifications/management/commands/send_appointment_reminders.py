from datetime import date, timedelta
from django.core.management.base import BaseCommand
from booking.models import Booking
from notifications.services import NotificationDispatcher


class Command(BaseCommand):
    help = "Dispatches 24-hour appointment reminder notifications via Email and WhatsApp to customers with upcoming confirmed salon appointments."

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days ahead to send reminders for (default: 1 day).'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        target_date = date.today() + timedelta(days=days_ahead)
        self.stdout.write(f"Searching for confirmed appointments scheduled for {target_date}...")

        upcoming_bookings = Booking.objects.filter(
            status=Booking.STATUS_CONFIRMED,
            appointment_date=target_date
        )

        total_count = upcoming_bookings.count()
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS(f"No confirmed appointments found for {target_date}."))
            return

        sent_count = 0
        for booking in upcoming_bookings:
            res = NotificationDispatcher.send_appointment_reminder(booking)
            if res.get('email') or res.get('whatsapp'):
                sent_count += 1
                self.stdout.write(f"  [OK] Reminder dispatched for Booking #{booking.reference} ({booking.customer_name})")
            else:
                self.stdout.write(f"  [SKIPPED/FAILED] Booking #{booking.reference} skipped or failed.")

        self.stdout.write(
            self.style.SUCCESS(f"Processed {total_count} upcoming appointments. Successfully dispatched {sent_count} reminders.")
        )
