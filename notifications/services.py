import logging
import json
import urllib.parse
import urllib.request
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import NotificationLog

logger = logging.getLogger(__name__)


class EmailChannelService:
    """
    Handles HTML and Plaintext email rendering and delivery.
    """

    @classmethod
    def send_email(cls, recipient_email, subject, template_prefix, context):
        """
        Renders HTML and text templates and dispatches email via Django's SMTP/console backend.
        """
        if not recipient_email:
            return False, "Recipient email is empty."

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Bolbash Beauty Spot <noreply@bolbash.com>')
        to_email = [recipient_email]

        try:
            html_content = render_to_string(f'emails/{template_prefix}.html', context)
            text_content = render_to_string(f'emails/{template_prefix}.txt', context)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            return True, None
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Email delivery failed to {recipient_email} for template {template_prefix}: {err_msg}")
            return False, err_msg


class WhatsAppChannelService:
    """
    Modular WhatsApp integration service.
    If API credentials are provided in settings, dispatches to WhatsApp API.
    Otherwise, formats, logs, and tracks formatted WhatsApp text messages cleanly in development/simulation mode.
    """

    @classmethod
    def send_whatsapp(cls, recipient_phone, message_text):
        """
        Dispatches WhatsApp message to recipient phone number.
        """
        if not recipient_phone:
            return False, "Recipient phone number is empty."

        api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)

        if api_url and api_token and phone_id:
            try:
                # Production WhatsApp Business Cloud API Integration via urllib
                url = f"{api_url}/{phone_id}/messages"
                headers = {
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                }
                payload = json.dumps({
                    "messaging_product": "whatsapp",
                    "to": recipient_phone,
                    "type": "text",
                    "text": {"body": message_text}
                }).encode('utf-8')

                req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status in [200, 201]:
                        return True, None
                    else:
                        return False, f"WhatsApp API HTTP {response.status}"
            except Exception as e:
                err_msg = str(e)
                logger.error(f"WhatsApp API HTTP dispatch error to {recipient_phone}: {err_msg}")
                return False, err_msg
        else:
            # Development/Simulation Mode Log
            logger.info(f"[WHATSAPP SIMULATION MODE] To: {recipient_phone}\nMessage:\n{message_text}")
            return True, None


class NotificationDispatcher:
    """
    Central event-driven notification architecture for Bolbash Beauty Spot.
    Handles multi-channel dispatching (Email & WhatsApp), idempotency, log recording, and fault isolation.
    """

    @classmethod
    def dispatch_event(cls, notification_type, target_object, recipient_email, recipient_phone, email_subject, template_prefix, context, whatsapp_text):
        """
        Generic multi-channel dispatch engine.
        Enforces idempotency per channel and catches errors gracefully.
        """
        booking_obj = target_object if hasattr(target_object, 'reference') and target_object.__class__.__name__ == 'Booking' else None
        order_obj = target_object if hasattr(target_object, 'order_number') and target_object.__class__.__name__ == 'Order' else None
        enrollment_obj = target_object if hasattr(target_object, 'enrollment_status') and target_object.__class__.__name__ == 'Enrollment' else None
        certificate_obj = target_object if hasattr(target_object, 'certificate_id') and target_object.__class__.__name__ == 'Certificate' else None

        results = {'email': False, 'whatsapp': False}

        # 1. Dispatch Email Channel if recipient email exists
        if recipient_email:
            already_sent_email = NotificationLog.objects.filter(
                notification_type=notification_type,
                channel=NotificationLog.CHANNEL_EMAIL,
                recipient_email=recipient_email,
                status=NotificationLog.STATUS_SENT,
                booking=booking_obj,
                order=order_obj,
                enrollment=enrollment_obj,
                certificate=certificate_obj
            ).exists()

            if already_sent_email:
                logger.info(f"Email for {notification_type} to {recipient_email} already sent. Skipping duplicate.")
                results['email'] = True
            else:
                success, err = EmailChannelService.send_email(recipient_email, email_subject, template_prefix, context)
                NotificationLog.objects.create(
                    channel=NotificationLog.CHANNEL_EMAIL,
                    notification_type=notification_type,
                    recipient=recipient_email,
                    recipient_email=recipient_email,
                    booking=booking_obj,
                    order=order_obj,
                    enrollment=enrollment_obj,
                    certificate=certificate_obj,
                    subject_or_summary=email_subject,
                    status=NotificationLog.STATUS_SENT if success else NotificationLog.STATUS_FAILED,
                    error_message=err
                )
                results['email'] = success

        # 2. Dispatch WhatsApp Channel if recipient phone exists
        if recipient_phone and whatsapp_text:
            already_sent_wa = NotificationLog.objects.filter(
                notification_type=notification_type,
                channel=NotificationLog.CHANNEL_WHATSAPP,
                recipient=recipient_phone,
                status=NotificationLog.STATUS_SENT,
                booking=booking_obj,
                order=order_obj,
                enrollment=enrollment_obj,
                certificate=certificate_obj
            ).exists()

            if already_sent_wa:
                logger.info(f"WhatsApp for {notification_type} to {recipient_phone} already sent. Skipping duplicate.")
                results['whatsapp'] = True
            else:
                success, err = WhatsAppChannelService.send_whatsapp(recipient_phone, whatsapp_text)
                NotificationLog.objects.create(
                    channel=NotificationLog.CHANNEL_WHATSAPP,
                    notification_type=notification_type,
                    recipient=recipient_phone,
                    recipient_email=recipient_email,
                    booking=booking_obj,
                    order=order_obj,
                    enrollment=enrollment_obj,
                    certificate=certificate_obj,
                    subject_or_summary=whatsapp_text[:100],
                    status=NotificationLog.STATUS_SENT if success else NotificationLog.STATUS_FAILED,
                    error_message=err
                )
                results['whatsapp'] = success

        return results

    # --- SPECIFIC BUSINESS EVENT DISPATCHERS ---

    @classmethod
    def send_booking_confirmation(cls, booking):
        """Dispatches Booking Confirmation (Email + WhatsApp)"""
        subject = f"Your Bolbash Beauty Spot Appointment Is Confirmed — {booking.reference}"
        context = {'booking': booking}
        wa_text = (
            f"✨ *BOLBASH BEAUTY SPOT APPOINTMENT CONFIRMED*\n\n"
            f"Hello {booking.customer_name},\n"
            f"Your appointment is confirmed!\n\n"
            f"📌 *Ref:* #{booking.reference}\n"
            f"💇‍♀️ *Service:* {booking.service_name_snapshot}\n"
            f"📅 *Date:* {booking.appointment_date.strftime('%a, %b %d, %Y')}\n"
            f"⏰ *Time:* {booking.appointment_time}\n"
            f"📍 *Location:* SIOA Plaza, Sango-Eleyele Rd, Ibadan\n\n"
            f"Thank you for choosing Bolbash!"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_BOOKING_CONFIRMATION,
            target_object=booking,
            recipient_email=booking.customer_email,
            recipient_phone=booking.customer_phone,
            email_subject=subject,
            template_prefix='booking_confirmed',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_appointment_reminder(cls, booking):
        """Dispatches 24h Appointment Reminder (Email + WhatsApp)"""
        subject = f"Reminder: Upcoming Salon Appointment — {booking.reference}"
        context = {'booking': booking}
        wa_text = (
            f"⏰ *BOLBASH BEAUTY SPOT APPOINTMENT REMINDER*\n\n"
            f"Hello {booking.customer_name},\n"
            f"Reminder: You have an upcoming appointment tomorrow!\n\n"
            f"📌 *Ref:* #{booking.reference}\n"
            f"💇‍♀️ *Service:* {booking.service_name_snapshot}\n"
            f"📅 *Date:* {booking.appointment_date.strftime('%a, %b %d, %Y')}\n"
            f"⏰ *Time:* {booking.appointment_time}\n\n"
            f"Please arrive 10 minutes early. Contact us on WhatsApp if you have questions!"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_APPOINTMENT_REMINDER,
            target_object=booking,
            recipient_email=booking.customer_email,
            recipient_phone=booking.customer_phone,
            email_subject=subject,
            template_prefix='appointment_reminder',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_appointment_cancellation(cls, booking, cancelled_by="Administrator"):
        """Dispatches Appointment Cancellation (Email + WhatsApp)"""
        subject = f"Appointment Cancelled — {booking.reference}"
        context = {'booking': booking, 'cancelled_by': cancelled_by}
        wa_text = (
            f"❌ *BOLBASH BEAUTY SPOT CANCELLATION NOTICE*\n\n"
            f"Hello {booking.customer_name},\n"
            f"Your appointment #{booking.reference} for {booking.service_name_snapshot} on {booking.appointment_date.strftime('%b %d, %Y')} has been cancelled by {cancelled_by}.\n\n"
            f"Reply to this message to rebook at a convenient date!"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_APPOINTMENT_CANCELLATION,
            target_object=booking,
            recipient_email=booking.customer_email,
            recipient_phone=booking.customer_phone,
            email_subject=subject,
            template_prefix='appointment_cancelled',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_appointment_rescheduled(cls, booking, old_date=None, old_time=None):
        """Dispatches Appointment Rescheduling Notification (Email + WhatsApp)"""
        subject = f"Appointment Rescheduled — {booking.reference}"
        context = {'booking': booking, 'old_date': old_date, 'old_time': old_time}
        wa_text = (
            f"📅 *BOLBASH BEAUTY SPOT SCHEDULE UPDATED*\n\n"
            f"Hello {booking.customer_name},\n"
            f"Your appointment #{booking.reference} has been rescheduled.\n\n"
            f"💇‍♀️ *Service:* {booking.service_name_snapshot}\n"
            f"🆕 *New Date:* {booking.appointment_date.strftime('%a, %b %d, %Y')}\n"
            f"⏰ *New Time:* {booking.appointment_time}\n\n"
            f"We look forward to hosting you!"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_APPOINTMENT_RESCHEDULED,
            target_object=booking,
            recipient_email=booking.customer_email,
            recipient_phone=booking.customer_phone,
            email_subject=subject,
            template_prefix='appointment_rescheduled',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_post_appointment_review_request(cls, booking, domain=None):
        """
        Dispatches Post-Appointment Review Request notification (Email + WhatsApp)
        inviting the client to rate and review their completed salon appointment.
        Guards against duplicate review requests via NotificationLog idempotency check.
        """
        from django.urls import reverse

        # Check duplicate
        if NotificationLog.objects.filter(
            booking=booking,
            notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW,
            status=NotificationLog.STATUS_SENT
        ).exists():
            logger.info(f"Post-appointment review request already dispatched for booking #{booking.reference}. Skipping.")
            return True, "Already sent."

        review_path = reverse('accounts:submit_review', kwargs={'booking_id': booking.pk})
        review_url = f"{domain or ''}{review_path}"

        subject = f"How was your appointment at Bolbash Beauty Spot? Leave a Review ✨ — #{booking.reference}"
        context = {
            'booking': booking,
            'review_url': review_url,
        }

        wa_text = (
            f"👑 *HOW WAS YOUR EXPERIENCE AT BOLBASH BEAUTY SPOT?*\n\n"
            f"Hello {booking.customer_name},\n"
            f"Thank you for visiting Bolbash Beauty Spot for your {booking.service_name_snapshot}!\n\n"
            f"We hope you loved your service! Please take 60 seconds to share your review and rate your experience:\n"
            f"👉 {review_url}\n\n"
            f"Your feedback helps us continuously deliver world-class beauty services."
        )

        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_POST_APPOINTMENT_REVIEW,
            target_object=booking,
            recipient_email=booking.customer_email,
            recipient_phone=booking.customer_phone,
            email_subject=subject,
            template_prefix='review_request',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_academy_enrolment(cls, enrollment, student_phone=None):
        """Dispatches Academy Enrolment Welcome (Email + WhatsApp)"""
        student_name = enrollment.user.get_full_name() or enrollment.user.username
        if not student_phone:
            student_phone = getattr(getattr(enrollment.user, 'studentprofile', None), 'phone_number', '') or getattr(enrollment.user, 'phone', '')
        subject = f"Welcome to Bolbash Beauty Academy — {enrollment.course.title}"
        context = {'enrollment': enrollment, 'student_name': student_name}
        wa_text = (
            f"🎓 *WELCOME TO BOLBASH BEAUTY ACADEMY*\n\n"
            f"Hello {student_name},\n"
            f"Welcome aboard! Your enrolment in *{enrollment.course.title}* is confirmed.\n\n"
            f"Log in to your student dashboard to start learning right away:\n"
            f"http://127.0.0.1:8000/academy/dashboard/"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_ACADEMY_ENROLMENT,
            target_object=enrollment,
            recipient_email=enrollment.user.email,
            recipient_phone=student_phone,
            email_subject=subject,
            template_prefix='academy_enrolment',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_course_completion(cls, certificate, student_phone=None):
        """Dispatches Course Completion & Certificate Notification (Email + WhatsApp)"""
        student_name = certificate.user.get_full_name() or certificate.user.username
        if not student_phone:
            student_phone = getattr(getattr(certificate.user, 'studentprofile', None), 'phone_number', '') or getattr(certificate.user, 'phone', '')
        subject = f"Congratulations on Graduating — {certificate.course.title}"
        context = {'certificate': certificate, 'student_name': student_name}
        wa_text = (
            f"🎉 *CONGRATULATIONS GRADUATE!*\n\n"
            f"Hello {student_name},\n"
            f"You have completed 100% of *{certificate.course.title}*!\n\n"
            f"📜 *Certificate ID:* #{certificate.certificate_id}\n"
            f"View your official PDF certificate here:\n"
            f"http://127.0.0.1:8000/academy/certificates/{certificate.certificate_id}/"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_COURSE_COMPLETION,
            target_object=certificate,
            recipient_email=certificate.user.email,
            recipient_phone=student_phone,
            email_subject=subject,
            template_prefix='course_completion',
            context=context,
            whatsapp_text=wa_text
        )

    @classmethod
    def send_order_confirmation(cls, order):
        """Dispatches Shop Order Confirmation (Email + WhatsApp)"""
        subject = f"Shop Order Receipt — #{order.order_number}"
        context = {'order': order}
        wa_text = (
            f"🛍️ *BOLBASH BEAUTY SHOP ORDER CONFIRMED*\n\n"
            f"Hello {order.customer_name},\n"
            f"Thank you for your purchase! Order #{order.order_number} is confirmed.\n\n"
            f"📦 *Total Paid:* ₦{order.total_amount:,.2f}\n"
            f"🚚 *Shipping Address:* {order.shipping_address}\n\n"
            f"Track your order here:\n"
            f"http://127.0.0.1:8000/shop/orders/{order.order_number}/"
        )
        return cls.dispatch_event(
            notification_type=NotificationLog.TYPE_ORDER_CONFIRMATION,
            target_object=order,
            recipient_email=order.customer_email,
            recipient_phone=order.customer_phone,
            email_subject=subject,
            template_prefix='order_confirmation',
            context=context,
            whatsapp_text=wa_text
        )


class EmailNotificationService:
    """
    Backward-compatibility wrapper for existing codebase imports.
    """
    @classmethod
    def send_booking_confirmation_email(cls, booking):
        res = NotificationDispatcher.send_booking_confirmation(booking)
        return res.get('email', False)
