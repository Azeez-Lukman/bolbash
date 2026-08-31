import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from booking.models import Booking
from notifications.services import EmailNotificationService, NotificationDispatcher

# ... inside verify_payment view ...

from .models import Payment
from .services import PaystackService


def paystack_sandbox_checkout(request, payment_reference):
    """
    Renders an interactive Paystack Test Checkout Sandbox in development mode.
    Allows testing successful vs cancelled/failed payments without auto-confirming.
    """
    payment = get_object_or_404(Payment, reference=payment_reference)
    booking = payment.booking
    
    if request.method == 'POST':
        action = request.POST.get('action', 'success')
        if action == 'cancel':
            payment.status = Payment.STATUS_FAILED
            payment.gateway_response = "User cancelled test payment"
            payment.save()
            return redirect('payments:payment_failed', booking_reference=booking.reference if booking else 'NO_REF')

        # Direct, atomic mock payment completion for dev sandbox mode
        with transaction.atomic():
            payment.status = Payment.STATUS_PAID
            payment.paystack_reference = f"MOCK-PAY-{payment.reference}"
            payment.gateway_response = "Successful Mock Test Payment"
            payment.channel = "card"
            payment.paid_at = timezone.now()
            payment.save()

            if booking:
                booking.status = Booking.STATUS_CONFIRMED
                booking.payment_status = Booking.PAYMENT_PAID
                booking.save()
                NotificationDispatcher.send_booking_confirmation(booking)
                messages.success(request, "Payment verified successfully! Your appointment is now confirmed.")
                return redirect('booking:booking_confirmation', reference=booking.reference)
            elif payment.order:
                order = payment.order
                order.payment_status = 'PAID'
                order.order_status = 'PROCESSING'
                order.save()
                NotificationDispatcher.send_order_confirmation(order)
                messages.success(request, f"Payment verified successfully! Order #{order.order_number} is confirmed.")
                return redirect('shop:order_confirmation', order_number=order.order_number)
            elif payment.enrollment:
                enrollment = payment.enrollment
                enrollment.payment_status = 'PAID'
                enrollment.enrollment_status = 'ACTIVE'
                enrollment.save()
                NotificationDispatcher.send_academy_enrolment(enrollment)
                messages.success(request, f"Payment verified successfully! You are enrolled in {enrollment.course.title}.")
                return redirect('academy:enrollment_confirmation', slug=enrollment.course.slug)

        callback_url = reverse('payments:verify_payment') + f"?payment_ref={payment.reference}&trxref={payment.reference}"
        return redirect(callback_url)

    context = {
        'payment': payment,
        'booking': booking,
    }
    return render(request, 'payments/sandbox_checkout.html', context)


def initiate_payment(request, booking_reference):
    """
    Initializes a Paystack payment session for a given booking.
    Calculates exact amount server-side to prevent price manipulation.
    """
    booking = get_object_or_404(Booking, reference=booking_reference)

    # Security Check: Prevent double-paying confirmed bookings
    if booking.status == Booking.STATUS_CONFIRMED and booking.payment_status == Booking.PAYMENT_PAID:
        messages.info(request, "This booking has already been paid and confirmed.")
        return redirect('booking:booking_confirmation', reference=booking.reference)

    # Determine authoritative amount server-side (never from client input)
    amount = booking.amount_due or booking.service_price_snapshot or 0
    
    try:
        amount_val = float(amount)
    except (ValueError, TypeError):
        amount_val = 0.0

    amount_kobo = int(amount_val * 100)

    # Create Payment instance
    payment = Payment.objects.create(
        booking=booking,
        amount=amount_val,
        currency='NGN',
        status=Payment.STATUS_PENDING
    )

    callback_url = request.build_absolute_uri(reverse('payments:verify_payment')) + f"?payment_ref={payment.reference}"

    try:
        res = PaystackService.initialize_transaction(
            email=booking.customer_email,
            amount_kobo=amount_kobo if amount_kobo > 0 else 100000,
            reference=payment.reference,
            callback_url=callback_url,
            metadata={
                'booking_reference': booking.reference,
                'payment_reference': payment.reference,
                'customer_name': booking.customer_name,
            }
        )

        if res.get('status'):
            auth_url = res['data']['authorization_url']
            payment.paystack_reference = res['data'].get('reference', payment.reference)
            payment.save()
            return redirect(auth_url)
        else:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, res.get('message', 'Failed to initialize payment session with Paystack.'))
            return redirect('payments:payment_failed', booking_reference=booking.reference)

    except Exception as e:
        payment.status = Payment.STATUS_FAILED
        payment.save()
        messages.error(request, f"Unable to initialize payment: {str(e)}")
        return redirect('payments:payment_failed', booking_reference=booking.reference)


def verify_payment(request):
    """
    Callback endpoint where Paystack redirects user after payment attempt.
    Independently verifies transaction with Paystack API server-side before confirming booking.
    Dispatches booking confirmation email upon successful verification.
    """
    raw_payment_ref = request.GET.get('payment_ref', '').split('?')[0].strip()
    raw_trxref = (request.GET.get('trxref') or request.GET.get('reference') or '').split('?')[0].strip()

    payment_ref = raw_payment_ref if raw_payment_ref else None
    trxref = raw_trxref if raw_trxref else None

    if not payment_ref and not trxref:
        messages.error(request, "Invalid payment callback request.")
        return redirect('core:index')

    payment = Payment.objects.filter(reference=payment_ref).first() if payment_ref else None
    if not payment and trxref:
        payment = Payment.objects.filter(paystack_reference=trxref).first() or Payment.objects.filter(reference=trxref).first()

    if not payment:
        messages.error(request, "Payment record not found.")
        return redirect('core:index')

    booking = payment.booking
    enrollment = payment.enrollment
    order = payment.order

    # Handle Shop Order Payment Verification
    if payment.payment_type == Payment.PAYMENT_TYPE_ORDER or order:
        from shop.models import Order
        if payment.status == Payment.STATUS_PAID and order.payment_status == Order.PAYMENT_PAID:
            messages.info(request, f"Order #{order.order_number} payment is already verified.")
            return redirect('shop:order_confirmation', order_number=order.order_number)

        try:
            verification_ref = trxref or payment.paystack_reference or payment.reference
            res = PaystackService.verify_transaction(verification_ref)

            if res.get('status') and res.get('data', {}).get('status') == 'success':
                data = res['data']
                with transaction.atomic():
                    payment.status = Payment.STATUS_PAID
                    payment.paystack_reference = data.get('reference', trxref)
                    payment.gateway_response = data.get('gateway_response', 'Success')
                    payment.channel = data.get('channel', 'card')
                    payment.paid_at = timezone.now()
                    payment.save()

                    order.payment_status = Order.PAYMENT_PAID
                    order.order_status = Order.STATUS_PROCESSING
                    order.save()

                    # Safely deduct inventory stock for ordered items
                    for item in order.items.select_related('product').all():
                        if item.product:
                            item.product.stock_quantity = max(0, item.product.stock_quantity - item.quantity)
                            item.product.save()

                    # Clear user/session cart after successful order payment
                    from shop.models import Cart
                    if order.user:
                        Cart.objects.filter(user=order.user).delete()
                    elif request.session.session_key:
                        Cart.objects.filter(session_key=request.session.session_key).delete()

                    # Dispatch Order Confirmation Notification
                    NotificationDispatcher.send_order_confirmation(order)

                messages.success(request, f"Payment verified successfully! Order #{order.order_number} is confirmed.")
                return redirect('shop:order_confirmation', order_number=order.order_number)
            else:
                payment.status = Payment.STATUS_FAILED
                payment.gateway_response = res.get('message', 'Payment failed')
                payment.save()
                messages.error(request, "Order payment verification failed. Please try again.")
                return redirect('shop:checkout')
        except Exception as e:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, f"Error verifying order payment: {str(e)}")
            return redirect('shop:checkout')

    # Handle Course Tuition Payment Verification
    if payment.payment_type == Payment.PAYMENT_TYPE_COURSE or enrollment:

        from academy.models import Enrollment
        if payment.status == Payment.STATUS_PAID and enrollment.payment_status == Enrollment.PAYMENT_PAID:
            NotificationDispatcher.send_academy_enrolment(enrollment)
            messages.info(request, f"Tuition payment for {enrollment.course.title} is already verified.")
            return redirect('academy:enrollment_confirmation', slug=enrollment.course.slug)

        try:
            verification_ref = trxref or payment.paystack_reference or payment.reference
            res = PaystackService.verify_transaction(verification_ref)

            if res.get('status') and res.get('data', {}).get('status') == 'success':
                data = res['data']
                with transaction.atomic():
                    payment.status = Payment.STATUS_PAID
                    payment.paystack_reference = data.get('reference', trxref)
                    payment.gateway_response = data.get('gateway_response', 'Success')
                    payment.channel = data.get('channel', 'card')
                    payment.paid_at = timezone.now()
                    payment.save()

                    enrollment.payment_status = Enrollment.PAYMENT_PAID
                    enrollment.enrollment_status = Enrollment.STATUS_ACTIVE
                    enrollment.save()

                NotificationDispatcher.send_academy_enrolment(enrollment)

                messages.success(request, f"Payment verified successfully! You are now actively enrolled in {enrollment.course.title}.")
                return redirect('academy:enrollment_confirmation', slug=enrollment.course.slug)
            else:
                payment.status = Payment.STATUS_FAILED
                payment.gateway_response = res.get('message', 'Payment failed')
                payment.save()
                messages.error(request, "Tuition payment verification failed. Please try again.")
                return redirect('academy:enrollment_confirmation', slug=enrollment.course.slug)
        except Exception as e:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, f"Error verifying course payment: {str(e)}")
            return redirect('academy:enrollment_confirmation', slug=enrollment.course.slug)

    # Handle Salon Booking Payment Verification
    if booking:
        if payment.status == Payment.STATUS_PAID and booking.status == Booking.STATUS_CONFIRMED:
            NotificationDispatcher.send_booking_confirmation(booking)
            return redirect('booking:booking_confirmation', reference=booking.reference)

        try:
            verification_ref = trxref or payment.paystack_reference or payment.reference
            res = PaystackService.verify_transaction(verification_ref)

            if res.get('status') and res.get('data', {}).get('status') == 'success':
                data = res['data']
                returned_currency = data.get('currency', 'NGN')
                if returned_currency != 'NGN':
                    payment.status = Payment.STATUS_FAILED
                    payment.save()
                    messages.error(request, "Currency mismatch detected.")
                    return redirect('payments:payment_failed', booking_reference=booking.reference)

                with transaction.atomic():
                    payment.status = Payment.STATUS_PAID
                    payment.paystack_reference = data.get('reference', trxref)
                    payment.gateway_response = data.get('gateway_response', 'Success')
                    payment.channel = data.get('channel', 'card')
                    payment.paid_at = timezone.now()
                    payment.save()

                    booking.status = Booking.STATUS_CONFIRMED
                    booking.payment_status = Booking.PAYMENT_PAID
                    booking.save()

                NotificationDispatcher.send_booking_confirmation(booking)

                messages.success(request, "Payment verified successfully! Your appointment is now confirmed.")
                return redirect('booking:booking_confirmation', reference=booking.reference)
            else:
                payment.status = Payment.STATUS_FAILED
                payment.gateway_response = res.get('message', 'Payment failed')
                payment.save()
                return redirect('payments:payment_failed', booking_reference=booking.reference)

        except Exception as e:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, f"Error verifying payment: {str(e)}")
            return redirect('payments:payment_failed', booking_reference=booking.reference)


def payment_failed(request, booking_reference):
    """
    Renders professional payment failure page with retry & WhatsApp support options.
    """
    booking = get_object_or_404(Booking, reference=booking_reference)
    context = {
        'booking': booking,
    }
    return render(request, 'payments/payment_failed.html', context)


@csrf_exempt
def paystack_webhook(request):
    """
    Secure Paystack Webhook listener.
    Verifies HMAC-SHA512 signature before processing charge.success events idempotently.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    signature = request.headers.get('x-paystack-signature')
    
    if not PaystackService.verify_webhook_signature(request.body, signature):
        return HttpResponse("Invalid Signature", status=400)

    try:
        event = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return HttpResponse("Invalid JSON", status=400)

    if event.get('event') == 'charge.success':
        data = event.get('data', {})
        paystack_ref = data.get('reference')
        
        payment = Payment.objects.filter(reference=paystack_ref).first() or Payment.objects.filter(paystack_reference=paystack_ref).first()

        if payment and payment.status != Payment.STATUS_PAID:
            with transaction.atomic():
                payment.status = Payment.STATUS_PAID
                payment.paystack_reference = paystack_ref
                payment.paid_at = timezone.now()
                payment.save()

                if payment.booking:
                    booking = payment.booking
                    booking.status = Booking.STATUS_CONFIRMED
                    booking.payment_status = Booking.PAYMENT_PAID
                    booking.save()
                    NotificationDispatcher.send_booking_confirmation(booking)
                elif payment.order:
                    order = payment.order
                    order.payment_status = Order.PAYMENT_PAID
                    order.order_status = Order.STATUS_PROCESSING
                    order.save()
                    NotificationDispatcher.send_order_confirmation(order)

    return HttpResponse(status=200)
