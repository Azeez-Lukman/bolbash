from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.db.models import Q, Count, Sum
from django.utils import timezone

from .models import CustomerProfile
from .forms import CustomerRegistrationForm, CustomerProfileForm, CustomerLoginForm
from booking.models import Booking
from shop.models import Order
from payments.models import Payment
from core.models import Review
from core.forms import ReviewForm


def register(request):
    """
    Handles customer registration at /accounts/register/.
    Creates standard User + CustomerProfile, auto-links guest bookings/orders matching email,
    and logs in automatically.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        post_next = request.POST.get('next', next_url)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data.get('address', '')
            city = form.cleaned_data.get('city', 'Ibadan')
            state = form.cleaned_data.get('state', 'Oyo State')
            password = form.cleaned_data['password']

            try:
                # Create User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Create CustomerProfile
                CustomerProfile.objects.create(
                    user=user,
                    phone_number=phone_number,
                    address=address,
                    city=city,
                    state=state
                )

                # Auto-link pre-existing guest bookings matching email
                Booking.objects.filter(customer_email__iexact=email, user__isnull=True).update(user=user)

                # Auto-link pre-existing guest shop orders matching email
                Order.objects.filter(customer_email__iexact=email, user__isnull=True).update(user=user)

                # Authenticate and login automatically
                login(request, user)
                messages.success(request, f"Welcome to Bolbash Beauty Spot, {first_name}! Your account has been created successfully.")

                if post_next:
                    return redirect(post_next)
                return redirect('accounts:dashboard')

            except IntegrityError:
                messages.error(request, "An account with this email address already exists.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'next': next_url,
    })


def login_view(request):
    """
    Handles customer login at /accounts/login/.
    Accepts email or username input.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        email_or_username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        post_next = request.POST.get('next', next_url)

        user = authenticate(request, username=email_or_username, password=password)

        if user is None and '@' in email_or_username:
            # Fallback: lookup user by email if email was entered
            try:
                user_obj = User.objects.get(email__iexact=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if post_next:
                    return redirect(post_next)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Your account is currently disabled. Please contact customer support.")
        else:
            messages.error(request, "Invalid email address or password. Please check your credentials and try again.")

    return render(request, 'accounts/login.html', {
        'next': next_url,
    })


def logout_view(request):
    """
    Logs out customer and redirects to index.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully. See you again soon!")
    return redirect('core:index')


@login_required(login_url='accounts:login')
def dashboard(request):
    """
    Central Customer Dashboard at /accounts/dashboard/.
    Provides overview statistics, next upcoming appointment, recent orders, and quick actions.
    """
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    today = timezone.now().date()

    # User's bookings (linked via ForeignKey or email match)
    user_bookings = Booking.objects.filter(
        Q(user=user) | Q(customer_email__iexact=user.email)
    ).distinct().select_related('service')

    total_appointments = user_bookings.count()
    
    upcoming_appointments = user_bookings.filter(
        appointment_date__gte=today
    ).exclude(status=Booking.STATUS_CANCELLED).order_by('appointment_date', 'appointment_time')
    
    upcoming_appointments_count = upcoming_appointments.count()
    completed_appointments_count = user_bookings.filter(status=Booking.STATUS_COMPLETED).count()

    # Next upcoming appointment snapshot
    next_appointment = upcoming_appointments.first()

    # User's shop orders
    user_orders = Order.objects.filter(
        Q(user=user) | Q(customer_email__iexact=user.email)
    ).distinct().order_by('-created_at')
    
    total_orders_count = user_orders.count()
    recent_orders = user_orders[:3]

    # User's payments
    user_payments = Payment.objects.filter(
        Q(booking__user=user) | Q(booking__customer_email__iexact=user.email) |
        Q(order__user=user) | Q(order__customer_email__iexact=user.email) |
        Q(enrollment__user=user)
    ).distinct().order_by('-created_at')
    
    total_payments_count = user_payments.count()
    total_spent = user_payments.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'profile': profile,
        'total_appointments': total_appointments,
        'upcoming_appointments_count': upcoming_appointments_count,
        'completed_appointments_count': completed_appointments_count,
        'total_orders_count': total_orders_count,
        'total_payments_count': total_payments_count,
        'total_spent': total_spent,
        'next_appointment': next_appointment,
        'recent_orders': recent_orders,
        'active_tab': 'dashboard',
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='accounts:login')
def upcoming_appointments(request):
    """
    Lists upcoming appointments for customer at /accounts/appointments/.
    """
    user = request.user
    today = timezone.now().date()

    user_bookings = Booking.objects.filter(
        Q(user=user) | Q(customer_email__iexact=user.email)
    ).distinct().select_related('service')

    upcoming_list = user_bookings.filter(
        appointment_date__gte=today
    ).exclude(status=Booking.STATUS_CANCELLED).order_by('appointment_date', 'appointment_time')

    context = {
        'bookings': upcoming_list,
        'view_mode': 'upcoming',
        'active_tab': 'appointments',
    }
    return render(request, 'accounts/appointments.html', context)


@login_required(login_url='accounts:login')
def appointment_history(request):
    """
    Lists appointment history (past, completed, cancelled) at /accounts/appointments/history/.
    """
    user = request.user
    today = timezone.now().date()

    user_bookings = Booking.objects.filter(
        Q(user=user) | Q(customer_email__iexact=user.email)
    ).distinct().select_related('service')

    history_list = user_bookings.filter(
        Q(appointment_date__lt=today) | Q(status__in=[Booking.STATUS_COMPLETED, Booking.STATUS_CANCELLED])
    ).order_by('-appointment_date', '-appointment_time')

    context = {
        'bookings': history_list,
        'view_mode': 'history',
        'active_tab': 'appointments',
    }
    return render(request, 'accounts/appointments.html', context)


@login_required(login_url='accounts:login')
def submit_review(request, booking_id):
    """
    Handles customer review submission for a completed salon appointment.
    Verifies user ownership, completion status, and ensures no duplicate review exists.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Ownership check
    is_owner = (booking.user == request.user) or (booking.customer_email.strip().lower() == request.user.email.strip().lower())
    if not is_owner:
        messages.error(request, "You are not authorized to review this appointment.")
        return redirect('accounts:appointment_history')

    # Completion status check
    if booking.status != Booking.STATUS_COMPLETED:
        messages.error(request, "Reviews can only be submitted for completed salon appointments.")
        return redirect('accounts:appointment_history')

    # Duplicate review check
    if hasattr(booking, 'review') and booking.review:
        messages.info(request, "You have already submitted a review for this appointment.")
        return redirect('accounts:appointment_history')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.booking = booking
            review.service = booking.service
            review.status = Review.STATUS_PENDING
            review.save()

            messages.success(request, "Thank you for your feedback! Your review has been submitted successfully for moderation.")
            return redirect('accounts:appointment_history')
        else:
            messages.error(request, "Please correct the errors below to submit your review.")
    else:
        form = ReviewForm()

    context = {
        'booking': booking,
        'form': form,
        'active_tab': 'appointments',
    }
    return render(request, 'accounts/submit_review.html', context)


@login_required(login_url='accounts:login')
def payment_history(request):
    """
    Customer payment history ledger at /accounts/payments/.
    Displays Paystack transaction payments for bookings, shop orders, and academy tuition.
    """
    user = request.user
    payment_type_filter = request.GET.get('type', 'all').upper()

    payments_query = Payment.objects.filter(
        Q(booking__user=user) | Q(booking__customer_email__iexact=user.email) |
        Q(order__user=user) | Q(order__customer_email__iexact=user.email) |
        Q(enrollment__user=user)
    ).distinct().order_by('-created_at')

    if payment_type_filter in ['BOOKING', 'ORDER', 'COURSE']:
        payments_query = payments_query.filter(payment_type=payment_type_filter)

    context = {
        'payments': payments_query,
        'current_type': payment_type_filter.lower(),
        'active_tab': 'payments',
    }
    return render(request, 'accounts/payments.html', context)


@login_required(login_url='accounts:login')
def profile_view(request):
    """
    Customer profile view and edit page at /accounts/profile/.
    """
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            # Update User object fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['email']
            user.save()

            # Save Profile fields
            form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerProfileForm(instance=profile, user=user)

    context = {
        'profile': profile,
        'form': form,
        'active_tab': 'profile',
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts:login')
def account_security(request):
    """
    Account security management at /accounts/security/.
    Includes password change form and security status summary.
    """
    user = request.user

    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            # Prevent user from being logged out after password change
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('accounts:security')
        else:
            messages.error(request, "Please correct the errors below to update your password.")
    else:
        form = PasswordChangeForm(user=user)

    context = {
        'form': form,
        'active_tab': 'security',
    }
    return render(request, 'accounts/security.html', context)


# Custom Password Reset Views styled with Bolbash Beauty Spot branding
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    subject_template_name = 'emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
