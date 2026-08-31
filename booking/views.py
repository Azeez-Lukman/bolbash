import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from .models import ServiceCategory, Service, BusinessHours, BlockedDate, Booking


def booking_form(request):
    """
    Renders the multi-step appointment booking interface.
    Supports pre-selecting a service via ?service=<slug>.
    """
    preselected_slug = request.GET.get('service', '').strip()
    selected_service = None

    if preselected_slug:
        selected_service = Service.objects.filter(slug=preselected_slug, active=True).first()

    categories = ServiceCategory.objects.prefetch_related('services').all()
    all_services = Service.objects.filter(active=True).select_related('category')

    context = {
        'categories': categories,
        'services': all_services,
        'selected_service': selected_service,
    }
    return render(request, 'booking/booking_form.html', context)


def api_available_slots(request):
    """
    AJAX endpoint returning available 60-minute time slots for a given service & date.
    Checks past dates, blocked dates, business hours, and existing bookings.
    """
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'slots': [], 'message': 'Please select a date.'})

    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'slots': [], 'message': 'Invalid date format.'})

    today = timezone.now().date()
    if selected_date < today:
        return JsonResponse({'slots': [], 'message': 'Past dates cannot be selected.'})

    # Check blocked dates
    if BlockedDate.objects.filter(date=selected_date, is_active=True).exists():
        return JsonResponse({'slots': [], 'message': 'The salon is closed on this date.'})

    # Check business hours
    weekday = selected_date.weekday()  # 0=Monday..6=Sunday
    b_hours = BusinessHours.objects.filter(day_of_week=weekday, is_active=True).first()

    if not b_hours:
        if weekday == 6:
            return JsonResponse({'slots': [], 'message': 'The salon is closed on Sundays.'})
        opening = datetime.time(9, 0)
        closing = datetime.time(18, 0)
    else:
        opening = b_hours.opening_time
        closing = b_hours.closing_time

    # Generate 1-hour interval slots
    slots = []
    current_time = datetime.datetime.combine(selected_date, opening)
    end_time_boundary = datetime.datetime.combine(selected_date, closing)

    fifteen_mins_ago = timezone.now() - datetime.timedelta(minutes=15)
    booked_times = set(
        Booking.objects.filter(
            appointment_date=selected_date
        ).filter(
            Q(status=Booking.STATUS_CONFIRMED) |
            (Q(status=Booking.STATUS_PENDING_PAYMENT) & Q(created_at__gte=fifteen_mins_ago))
        ).values_list('appointment_time', flat=True)
    )

    while current_time + datetime.timedelta(hours=1) <= end_time_boundary:
        t_slot = current_time.time()
        
        if selected_date == today and t_slot <= timezone.now().time():
            current_time += datetime.timedelta(hours=1)
            continue

        if t_slot not in booked_times:
            slots.append(t_slot.strftime('%H:%M'))
        
        current_time += datetime.timedelta(hours=1)

    if not slots:
        return JsonResponse({'slots': [], 'message': 'No appointment slots are available for this date. Please choose another date.'})

    return JsonResponse({'slots': slots, 'message': 'Slots available.'})


def booking_submit(request):
    """
    Handles form submission for new appointment creation.
    Performs server-side validation, double-booking prevention, and snapshot recording.
    Only confirmed bookings or active 15-minute pending holds create a slot conflict.
    """
    if request.method != 'POST':
        return redirect('booking:booking_form')

    service_id = request.POST.get('service_id')
    date_str = request.POST.get('appointment_date')
    time_str = request.POST.get('appointment_time')
    customer_name = request.POST.get('customer_name', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    customer_email = request.POST.get('customer_email', '').strip()
    customer_note = request.POST.get('customer_note', '').strip()

    if not all([service_id, date_str, time_str, customer_name, customer_phone, customer_email]):
        messages.error(request, "Please fill in all required fields.")
        return redirect('booking:booking_form')

    service = get_object_or_404(Service, id=service_id, active=True)

    try:
        appointment_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        appointment_time = datetime.datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        messages.error(request, "Invalid date or time selection.")
        return redirect('booking:booking_form')

    fifteen_mins_ago = timezone.now() - datetime.timedelta(minutes=15)
    with transaction.atomic():
        existing_conflict = Booking.objects.select_for_update().filter(
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(
            Q(status=Booking.STATUS_CONFIRMED) |
            (Q(status=Booking.STATUS_PENDING_PAYMENT) & Q(created_at__gte=fifteen_mins_ago))
        ).exists()

        if existing_conflict:
            messages.error(request, "That appointment time is currently held or confirmed by another client. Please choose another available time.")
            return redirect(f"{request.META.get('HTTP_REFERER', '/booking/')}?service={service.slug}")

        duration_mins = service.duration or 60
        start_datetime = datetime.datetime.combine(appointment_date, appointment_time)
        end_datetime = start_datetime + datetime.timedelta(minutes=duration_mins)
        end_time = end_datetime.time()

        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            service=service,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_note=customer_note,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            end_time=end_time,
            service_name_snapshot=service.name,
            service_price_snapshot=service.price,
            service_duration_snapshot=service.duration,
            status=Booking.STATUS_PENDING_PAYMENT,
            payment_status=Booking.PAYMENT_UNPAID,
            amount_due=getattr(settings, 'BOOKING_DEPOSIT_AMOUNT', 100.00),
        )

    return redirect('booking:booking_confirmation', reference=booking.reference)


def booking_confirmation(request, reference):
    """
    Renders the appointment confirmation summary page.
    """
    booking = get_object_or_404(Booking, reference=reference)
    context = {
        'booking': booking,
    }
    return render(request, 'booking/booking_confirmation.html', context)


def booking_lookup(request):
    """
    Renders guest-based customer booking lookup form and processes dual-factor verification queries.
    Requires Booking Reference + Email or Phone number to retrieve booking status.
    Protects privacy by returning a generic error message when details do not match.
    """
    booking = None
    searched = False
    error_message = None

    if request.method == 'POST':
        searched = True
        reference_input = request.POST.get('reference', '').strip()
        contact_input = request.POST.get('contact_info', '').strip()

        if not reference_input or not contact_input:
            error_message = "Please enter both your Booking Reference and your Email Address or Phone Number."
        else:
            # Perform strict dual-factor lookup (Case-insensitive reference & contact)
            booking = Booking.objects.filter(
                reference__iexact=reference_input
            ).filter(
                Q(customer_email__iexact=contact_input) | Q(customer_phone__icontains=contact_input)
            ).first()

            if not booking:
                # Privacy-preserving generic error message
                error_message = "We couldn't find an appointment matching those details. Please check your information and try again."

    context = {
        'booking': booking,
        'searched': searched,
        'error_message': error_message,
        'reference_input': request.POST.get('reference', '') if request.method == 'POST' else '',
        'contact_input': request.POST.get('contact_info', '') if request.method == 'POST' else '',
    }
    return render(request, 'booking/booking_lookup.html', context)
