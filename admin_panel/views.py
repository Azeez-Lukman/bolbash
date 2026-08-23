from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone

from notifications.services import NotificationDispatcher
from .decorators import admin_required
from booking.models import ServiceCategory, Service, BusinessHours, BlockedDate, Booking
from academy.models import CourseCategory, Course, Module, Lesson, LessonProgress, Enrollment, Certificate, StudentProfile
from shop.models import ProductCategory, Product, Order, OrderItem
from payments.models import Payment
from .forms import (
    ServiceForm, ServiceCategoryForm, BusinessHoursForm, BlockedDateForm, BookingStatusForm,
    CourseCategoryForm, CourseForm, ModuleForm, LessonForm, ProductCategoryForm, ProductForm,
    StockUpdateForm, OrderStatusForm
)


# ==============================================================================
# 1. CENTRAL ADMIN DASHBOARD
# ==============================================================================
@admin_required
def dashboard(request):
    """
    Central overview dashboard presenting immediate business metrics.
    """
    today = date.today()
    now = timezone.now()
    
    # Today's Appointments
    todays_bookings = Booking.objects.filter(appointment_date=today).order_by('appointment_time')
    todays_appointments_count = todays_bookings.count()
    
    # Upcoming Appointments
    upcoming_bookings = Booking.objects.filter(
        Q(appointment_date__gt=today) | Q(appointment_date=today, appointment_time__gte=now.time())
    ).order_by('appointment_date', 'appointment_time')[:6]
    
    # Verified Revenue Calculation (strictly Payment.STATUS_PAID)
    paid_payments = Payment.objects.filter(status=Payment.STATUS_PAID)
    
    today_revenue = paid_payments.filter(paid_at__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    
    start_of_week = today - timedelta(days=today.weekday())
    week_revenue = paid_payments.filter(paid_at__date__gte=start_of_week).aggregate(Sum('amount'))['amount__sum'] or 0
    
    start_of_month = today.replace(day=1)
    month_revenue = paid_payments.filter(paid_at__date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_revenue = paid_payments.aggregate(Sum('amount'))['amount__sum'] or 0

    # Recent Shop Orders
    recent_orders = Order.objects.all().order_by('-created_at')[:6]

    # Student & Academy Metrics
    total_students = StudentProfile.objects.count()
    active_enrolments = Enrollment.objects.filter(enrollment_status=Enrollment.STATUS_ACTIVE).count()
    total_courses = Course.objects.count()
    certificates_issued = Certificate.objects.filter(is_active=True).count()

    context = {
        'today': today,
        'todays_bookings': todays_bookings,
        'todays_appointments_count': todays_appointments_count,
        'upcoming_bookings': upcoming_bookings,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'total_students': total_students,
        'active_enrolments': active_enrolments,
        'total_courses': total_courses,
        'certificates_issued': certificates_issued,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ==============================================================================
# 2. APPOINTMENT MANAGEMENT
# ==============================================================================
@admin_required
def appointment_list(request):
    """
    Searchable, filterable list of all salon appointments.
    """
    queryset = Booking.objects.all().order_by('-appointment_date', '-appointment_time')
    
    # Search Query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(reference__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_email__icontains=q) |
            Q(customer_phone__icontains=q)
        )
        
    # Status Filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Date Filter (today, upcoming, past)
    date_filter = request.GET.get('date_filter', '').strip()
    today = date.today()
    if date_filter == 'today':
        queryset = queryset.filter(appointment_date=today)
    elif date_filter == 'upcoming':
        queryset = queryset.filter(appointment_date__gte=today)
    elif date_filter == 'past':
        queryset = queryset.filter(appointment_date__lt=today)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    bookings_page = paginator.get_page(page_number)

    context = {
        'bookings': bookings_page,
        'q': q,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/appointments/appointment_list.html', context)


@admin_required
def appointment_detail(request, reference):
    """
    Detailed appointment breakdown view with status update capabilities.
    """
    booking = get_object_or_404(Booking, reference=reference)
    form = BookingStatusForm(instance=booking)

    if request.method == 'POST':
        form = BookingStatusForm(request.POST, instance=booking)
        old_status = booking.status
        if form.is_valid():
            updated_booking = form.save()
            if old_status != Booking.STATUS_CANCELLED and updated_booking.status == Booking.STATUS_CANCELLED:
                NotificationDispatcher.send_appointment_cancellation(updated_booking, cancelled_by="Administrator")
            elif old_status != Booking.STATUS_COMPLETED and updated_booking.status == Booking.STATUS_COMPLETED:
                NotificationDispatcher.send_post_appointment_review_request(updated_booking)
            messages.success(request, f"Appointment #{booking.reference} status updated successfully.")
            return redirect('admin_panel:appointment_detail', reference=booking.reference)

    payments = Payment.objects.filter(booking=booking).order_by('-created_at')

    context = {
        'booking': booking,
        'form': form,
        'payments': payments,
    }
    return render(request, 'admin_panel/appointments/appointment_detail.html', context)


@admin_required
def appointment_reschedule(request, reference):
    """
    Reschedule an existing booking to a new available date & time slot.
    Calculates time slot conflicts to prevent double-booking.
    """
    booking = get_object_or_404(Booking, reference=reference)
    error_message = None

    if request.method == 'POST':
        new_date_str = request.POST.get('appointment_date')
        new_time_str = request.POST.get('appointment_time')

        if not new_date_str or not new_time_str:
            error_message = "Please select both a valid date and time slot."
        else:
            try:
                new_date = date.fromisoformat(new_date_str)
                # Check for blocked date
                if BlockedDate.objects.filter(date=new_date, is_active=True).exists():
                    error_message = f"The selected date ({new_date}) is blocked for salon bookings."
                else:
                    # Check for conflicting active bookings (excluding current booking)
                    conflicts = Booking.objects.filter(
                        appointment_date=new_date,
                        appointment_time=new_time_str
                    ).exclude(id=booking.id).exclude(status=Booking.STATUS_CANCELLED)

                    if conflicts.exists():
                        error_message = "This time slot is already booked. Please choose a different slot."
                    else:
                        old_date = booking.appointment_date
                        old_time = booking.appointment_time
                        booking.appointment_date = new_date
                        booking.appointment_time = new_time_str
                        booking.save()

                        # Dispatch Rescheduling Notification
                        NotificationDispatcher.send_appointment_rescheduled(booking, old_date=old_date, old_time=old_time)

                        messages.success(request, f"Appointment #{booking.reference} rescheduled to {new_date} at {new_time_str}.")
                        return redirect('admin_panel:appointment_detail', reference=booking.reference)
            except ValueError:
                error_message = "Invalid date format provided."

    context = {
        'booking': booking,
        'error_message': error_message,
        'today': date.today(),
    }
    return render(request, 'admin_panel/appointments/reschedule.html', context)


@admin_required
def availability_management(request):
    """
    Manage business operating hours for each day of the week.
    """
    hours = BusinessHours.objects.all().order_by('day_of_week')
    
    if request.method == 'POST':
        for item in hours:
            day_prefix = f"day_{item.day_of_week}_"
            is_active = request.POST.get(day_prefix + 'active') == 'on'
            opening_time = request.POST.get(day_prefix + 'opening')
            closing_time = request.POST.get(day_prefix + 'closing')

            if opening_time and closing_time:
                item.is_active = is_active
                item.opening_time = opening_time
                item.closing_time = closing_time
                item.save()

        messages.success(request, "Studio business operating hours updated successfully.")
        return redirect('admin_panel:availability')

    context = {'hours': hours}
    return render(request, 'admin_panel/appointments/availability.html', context)


@admin_required
def blocked_dates_management(request):
    """
    Manage calendar dates blocked from customer appointment booking.
    """
    blocked_dates = BlockedDate.objects.all().order_by('date')
    form = BlockedDateForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            form = BlockedDateForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Date blocked successfully.")
                return redirect('admin_panel:blocked_dates')
        elif action == 'delete':
            blocked_id = request.POST.get('blocked_id')
            item = get_object_or_404(BlockedDate, id=blocked_id)
            item.delete()
            messages.success(request, "Blocked date removed.")
            return redirect('admin_panel:blocked_dates')

    context = {
        'blocked_dates': blocked_dates,
        'form': form,
    }
    return render(request, 'admin_panel/appointments/blocked_dates.html', context)


# ==============================================================================
# 3. CUSTOMER MANAGEMENT
# ==============================================================================
@admin_required
def customer_list(request):
    """
    Searchable index of all registered customer & student user accounts.
    """
    queryset = User.objects.annotate(
        enrolment_count=Count('enrollments', distinct=True),
        order_count=Count('orders', distinct=True)
    ).order_by('-date_joined')

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter == 'active':
        queryset = queryset.filter(is_active=True)
    elif status_filter == 'suspended':
        queryset = queryset.filter(is_active=False)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)

    context = {
        'customers': customers_page,
        'q': q,
        'status_filter': status_filter,
    }
    return render(request, 'admin_panel/customers/customer_list.html', context)


@admin_required
def customer_detail(request, user_id):
    """
    Detailed profile view for a customer account consolidating bookings, orders, and enrolments.
    Allows staff to toggle active/suspended status safely.
    """
    customer = get_object_or_404(User, id=user_id)

    if request.method == 'POST' and 'toggle_active' in request.POST:
        # Prevent self-deactivation
        if customer.id == request.user.id:
            messages.error(request, "You cannot suspend your own administrative account.")
        else:
            customer.is_active = not customer.is_active
            customer.save()
            status_text = "activated" if customer.is_active else "suspended"
            messages.success(request, f"User account '{customer.username}' has been {status_text}.")
        return redirect('admin_panel:customer_detail', user_id=customer.id)

    bookings = Booking.objects.filter(customer_email=customer.email).order_by('-appointment_date')
    orders = Order.objects.filter(Q(user=customer) | Q(customer_email=customer.email)).order_by('-created_at')
    enrolments = Enrollment.objects.filter(user=customer).order_by('-created_at')
    certificates = Certificate.objects.filter(user=customer)

    context = {
        'customer': customer,
        'bookings': bookings,
        'orders': orders,
        'enrolments': enrolments,
        'certificates': certificates,
    }
    return render(request, 'admin_panel/customers/customer_detail.html', context)


# ==============================================================================
# 4. ACADEMY MANAGEMENT
# ==============================================================================
@admin_required
def academy_course_list(request):
    """
    List and manage training courses offered by Bolbash Beauty Academy.
    """
    courses = Course.objects.all().order_by('-created_at')
    context = {'courses': courses}
    return render(request, 'admin_panel/academy/course_list.html', context)


@admin_required
def academy_course_create(request):
    """
    Create a new academy course.
    """
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.title}' created successfully.")
            return redirect('admin_panel:academy_course_list')

    context = {'form': form, 'title': 'Create New Training Course'}
    return render(request, 'admin_panel/academy/course_form.html', context)


@admin_required
def academy_course_edit(request, course_id):
    """
    Edit existing academy course.
    """
    course = get_object_or_404(Course, id=course_id)
    form = CourseForm(instance=course)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully.")
            return redirect('admin_panel:academy_course_list')

    context = {'form': form, 'course': course, 'title': f"Edit Course: {course.title}"}
    return render(request, 'admin_panel/academy/course_form.html', context)


@admin_required
def academy_module_list(request, course_id=None):
    """
    Manage modules inside academy courses.
    """
    courses = Course.objects.all()
    selected_course = None
    if course_id:
        selected_course = get_object_or_404(Course, id=course_id)
        modules = Module.objects.filter(course=selected_course).order_by('order')
    else:
        modules = Module.objects.all().order_by('course', 'order')

    form = ModuleForm(initial={'course': selected_course} if selected_course else None)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            mod = form.save()
            messages.success(request, f"Module '{mod.title}' created successfully.")
            return redirect('admin_panel:academy_module_list_by_course', course_id=mod.course.id)

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'modules': modules,
        'form': form,
    }
    return render(request, 'admin_panel/academy/module_list.html', context)


@admin_required
def academy_lesson_list(request, module_id=None):
    """
    Manage lessons inside course modules.
    """
    modules = Module.objects.all()
    selected_module = None
    if module_id:
        selected_module = get_object_or_404(Module, id=module_id)
        lessons = Lesson.objects.filter(module=selected_module).order_by('order')
    else:
        lessons = Lesson.objects.all().order_by('module', 'order')

    form = LessonForm(initial={'module': selected_module} if selected_module else None)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            les = form.save()
            messages.success(request, f"Lesson '{les.title}' created successfully.")
            return redirect('admin_panel:academy_lesson_list_by_module', module_id=les.module.id)

    context = {
        'modules': modules,
        'selected_module': selected_module,
        'lessons': lessons,
        'form': form,
    }
    return render(request, 'admin_panel/academy/lesson_list.html', context)


@admin_required
def academy_student_list(request):
    """
    List enrolled academy students and monitor their learning metrics.
    """
    enrolments = Enrollment.objects.all().select_related('user', 'course').order_by('-created_at')
    context = {'enrolments': enrolments}
    return render(request, 'admin_panel/academy/student_list.html', context)


@admin_required
def academy_certificate_list(request):
    """
    List and verify graduation certificates issued to academy students.
    """
    certificates = Certificate.objects.all().select_related('user', 'course').order_by('-issue_date')
    
    q = request.GET.get('q', '').strip()
    if q:
        certificates = certificates.filter(
            Q(certificate_id__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q)
        )

    if request.method == 'POST' and 'toggle_active' in request.POST:
        cert_id = request.POST.get('cert_id')
        cert = get_object_or_404(Certificate, id=cert_id)
        cert.is_active = not cert.is_active
        cert.save()
        status_txt = "activated" if cert.is_active else "revoked/disabled"
        messages.success(request, f"Certificate #{cert.certificate_number} status set to {status_txt}.")
        return redirect('admin_panel:academy_certificates')

    context = {
        'certificates': certificates,
        'q': q,
    }
    return render(request, 'admin_panel/academy/certificate_list.html', context)


# ==============================================================================
# 5. SHOP & INVENTORY MANAGEMENT
# ==============================================================================
@admin_required
def shop_product_list(request):
    """
    List products in online shop with search, category & stock status filters.
    """
    products = Product.objects.all().order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(short_description__icontains=q))

    cat_slug = request.GET.get('category', '').strip()
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    stock_status = request.GET.get('stock', '').strip()
    if stock_status == 'in_stock':
        products = products.filter(stock_quantity__gt=0, is_active=True)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock_quantity=0)

    categories = ProductCategory.objects.filter(active=True)

    context = {
        'products': products,
        'categories': categories,
        'q': q,
        'cat_slug': cat_slug,
        'stock_status': stock_status,
    }
    return render(request, 'admin_panel/shop/product_list.html', context)


@admin_required
def shop_product_create(request):
    """
    Create a new product for online shop.
    """
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created successfully.")
            return redirect('admin_panel:shop_product_list')

    context = {'form': form, 'title': 'Add New Shop Product'}
    return render(request, 'admin_panel/shop/product_form.html', context)


@admin_required
def shop_product_edit(request, product_id):
    """
    Edit existing product details and stock.
    """
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(instance=product)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('admin_panel:shop_product_list')

    context = {'form': form, 'product': product, 'title': f"Edit Product: {product.name}"}
    return render(request, 'admin_panel/shop/product_form.html', context)


@admin_required
def shop_inventory_list(request):
    """
    Dedicated inventory management view for quick stock adjustments.
    Prevents negative stock levels.
    """
    products = Product.objects.all().order_by('stock_quantity', 'name')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock_str = request.POST.get('stock_quantity')
        
        try:
            new_stock = int(new_stock_str)
            if new_stock < 0:
                messages.error(request, "Stock quantity cannot be negative.")
            else:
                product = get_object_or_404(Product, id=product_id)
                product.stock_quantity = new_stock
                product.save()
                messages.success(request, f"Inventory stock for '{product.name}' updated to {new_stock}.")
        except (TypeError, ValueError):
            messages.error(request, "Invalid stock value entered.")

        return redirect('admin_panel:shop_inventory')

    context = {'products': products}
    return render(request, 'admin_panel/shop/inventory_list.html', context)


@admin_required
def shop_order_list(request):
    """
    List and filter customer shop orders.
    """
    orders = Order.objects.all().order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_email__icontains=q) |
            Q(customer_phone__icontains=q)
        )

    order_status = request.GET.get('order_status', '').strip()
    if order_status:
        orders = orders.filter(order_status=order_status)

    payment_status = request.GET.get('payment_status', '').strip()
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    paginator = Paginator(orders, 15)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    context = {
        'orders': orders_page,
        'q': q,
        'order_status': order_status,
        'payment_status': payment_status,
        'order_status_choices': Order.ORDER_STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'admin_panel/shop/order_list.html', context)


@admin_required
def shop_order_detail(request, order_number):
    """
    Detailed order receipt and fulfilment status manager.
    """
    order = get_object_or_404(Order, order_number=order_number)
    form = OrderStatusForm(instance=order)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.order_number} status updated successfully.")
            return redirect('admin_panel:shop_order_detail', order_number=order.order_number)

    payments = Payment.objects.filter(order=order).order_by('-created_at')

    context = {
        'order': order,
        'form': form,
        'payments': payments,
    }
    return render(request, 'admin_panel/shop/order_detail.html', context)


# ==============================================================================
# 6. NOTIFICATION SYSTEM DASHBOARD & RETRY
# ==============================================================================
@admin_required
def notification_list(request):
    """
    Searchable, filterable audit log of all system notifications (Email & WhatsApp).
    """
    from notifications.models import NotificationLog
    logs = NotificationLog.objects.all().order_by('-sent_at')

    q = request.GET.get('q', '').strip()
    if q:
        logs = logs.filter(
            Q(recipient__icontains=q) |
            Q(recipient_email__icontains=q) |
            Q(subject_or_summary__icontains=q)
        )

    channel_filter = request.GET.get('channel', '').strip()
    if channel_filter:
        logs = logs.filter(channel=channel_filter)

    type_filter = request.GET.get('type', '').strip()
    if type_filter:
        logs = logs.filter(notification_type=type_filter)

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        logs = logs.filter(status=status_filter)

    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    context = {
        'logs': logs_page,
        'q': q,
        'channel_filter': channel_filter,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'channel_choices': NotificationLog.CHANNEL_CHOICES,
        'type_choices': NotificationLog.TYPE_CHOICES,
        'status_choices': NotificationLog.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/notifications/notification_list.html', context)


@admin_required
def notification_retry(request, pk):
    """
    Manually retries dispatching a failed notification log entry.
    """
    from notifications.models import NotificationLog
    from notifications.services import NotificationDispatcher, EmailChannelService, WhatsAppChannelService

    log_entry = get_object_or_404(NotificationLog, pk=pk)

    if log_entry.status == NotificationLog.STATUS_SENT:
        messages.info(request, "This notification was already sent successfully.")
        return redirect('admin_panel:notification_list')

    success = False
    err_msg = None

    if log_entry.channel == NotificationLog.CHANNEL_EMAIL:
        if log_entry.booking:
            res = NotificationDispatcher.send_booking_confirmation(log_entry.booking)
            success = res.get('email', False)
        elif log_entry.order:
            res = NotificationDispatcher.send_order_confirmation(log_entry.order)
            success = res.get('email', False)
        elif log_entry.enrollment:
            res = NotificationDispatcher.send_academy_enrolment(log_entry.enrollment)
            success = res.get('email', False)
        elif log_entry.certificate:
            res = NotificationDispatcher.send_course_completion(log_entry.certificate)
            success = res.get('email', False)
    elif log_entry.channel == NotificationLog.CHANNEL_WHATSAPP:
        success, err_msg = WhatsAppChannelService.send_whatsapp(log_entry.recipient, log_entry.subject_or_summary or "Bolbash Beauty Spot Notification")

    if success:
        log_entry.status = NotificationLog.STATUS_SENT
        log_entry.error_message = None
        log_entry.save()
        messages.success(request, f"Notification retry succeeded for {log_entry.recipient}.")
    else:
        log_entry.status = NotificationLog.STATUS_FAILED
        log_entry.error_message = err_msg or "Retry failed."
        log_entry.save()
        messages.error(request, f"Notification retry failed for {log_entry.recipient}.")

    return redirect('admin_panel:notification_list')


# ==============================================================================
# 7. CUSTOMER ENQUIRIES DASHBOARD & STATUS MANAGEMENT
# ==============================================================================
@admin_required
def enquiry_list(request):
    """
    List, filter, and search customer contact form enquiries.
    """
    from core.models import ContactSubmission
    enquiries = ContactSubmission.objects.all().order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        enquiries = enquiries.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(subject__icontains=q) |
            Q(message__icontains=q)
        )

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        enquiries = enquiries.filter(status=status_filter)

    paginator = Paginator(enquiries, 15)
    page_number = request.GET.get('page')
    enquiries_page = paginator.get_page(page_number)

    context = {
        'enquiries': enquiries_page,
        'q': q,
        'status_filter': status_filter,
        'status_choices': ContactSubmission.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/enquiry_list.html', context)


@admin_required
def enquiry_update_status(request, pk):
    """
    Updates the status of a customer contact enquiry (NEW, IN_PROGRESS, RESPONDED, CLOSED).
    """
    from core.models import ContactSubmission
    enquiry = get_object_or_404(ContactSubmission, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        valid_statuses = [choice[0] for choice in ContactSubmission.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f"Enquiry from {enquiry.name} updated to status '{enquiry.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status choice selected.")

    return redirect('admin_panel:enquiry_list')


@admin_required
def review_list(request):
    """
    Lists customer reviews in the Admin Portal for moderation.
    Allows filtering by moderation status (PENDING, APPROVED, REJECTED) and search.
    """
    from core.models import Review

    reviews = Review.objects.select_related('user', 'booking', 'service').order_by('-created_at')

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        reviews = reviews.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(booking__reference__icontains=q) |
            Q(comment__icontains=q)
        )

    # Status filter
    status_filter = request.GET.get('status', '').strip().upper()
    if status_filter in [choice[0] for choice in Review.STATUS_CHOICES]:
        reviews = reviews.filter(status=status_filter)

    # Stats for counter badges
    all_count = Review.objects.count()
    pending_count = Review.objects.filter(status=Review.STATUS_PENDING).count()
    approved_count = Review.objects.filter(status=Review.STATUS_APPROVED).count()
    rejected_count = Review.objects.filter(status=Review.STATUS_REJECTED).count()

    paginator = Paginator(reviews, 15)
    page_number = request.GET.get('page')
    reviews_page = paginator.get_page(page_number)

    context = {
        'reviews': reviews_page,
        'q': q,
        'status_filter': status_filter,
        'status_choices': Review.STATUS_CHOICES,
        'all_count': all_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'active_tab': 'reviews',
    }
    return render(request, 'admin_panel/reviews/review_list.html', context)


@admin_required
def review_update_status(request, pk):
    """
    Updates the moderation status of a customer review (PENDING, APPROVED, REJECTED).
    Requires staff/admin authorization (@admin_required) and validates choices server-side.
    """
    from core.models import Review
    review = get_object_or_404(Review, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip().upper()
        valid_statuses = [choice[0] for choice in Review.STATUS_CHOICES]

        if new_status in valid_statuses:
            review.status = new_status
            review.save()
            customer_name = review.user.get_full_name() or review.user.username
            messages.success(request, f"Review by {customer_name} updated to status '{review.get_status_display()}'.")
        else:
            messages.error(request, "Invalid moderation status choice selected.")

    next_url = request.POST.get('next', '') or request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('admin_panel:review_list')


@admin_required
def feedback_list(request):
    """
    Lists customer feedback submissions in the Admin Portal.
    Allows filtering by status (NEW, IN_REVIEW, RESOLVED, CLOSED), category, and search.
    """
    from core.models import CustomerFeedback

    feedbacks = CustomerFeedback.objects.select_related('user').order_by('-created_at')

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        feedbacks = feedbacks.filter(
            Q(name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(subject__icontains=q) |
            Q(message__icontains=q) |
            Q(admin_notes__icontains=q)
        )

    # Status filter
    status_filter = request.GET.get('status', '').strip().upper()
    if status_filter in [choice[0] for choice in CustomerFeedback.STATUS_CHOICES]:
        feedbacks = feedbacks.filter(status=status_filter)

    # Category filter
    category_filter = request.GET.get('category', '').strip().upper()
    if category_filter in [choice[0] for choice in CustomerFeedback.CATEGORY_CHOICES]:
        feedbacks = feedbacks.filter(category=category_filter)

    # Stats for counter badges
    all_count = CustomerFeedback.objects.count()
    new_count = CustomerFeedback.objects.filter(status=CustomerFeedback.STATUS_NEW).count()
    in_review_count = CustomerFeedback.objects.filter(status=CustomerFeedback.STATUS_IN_REVIEW).count()
    resolved_count = CustomerFeedback.objects.filter(status=CustomerFeedback.STATUS_RESOLVED).count()

    paginator = Paginator(feedbacks, 15)
    page_number = request.GET.get('page')
    feedbacks_page = paginator.get_page(page_number)

    context = {
        'feedbacks': feedbacks_page,
        'q': q,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': CustomerFeedback.STATUS_CHOICES,
        'category_choices': CustomerFeedback.CATEGORY_CHOICES,
        'all_count': all_count,
        'new_count': new_count,
        'in_review_count': in_review_count,
        'resolved_count': resolved_count,
        'active_tab': 'feedback',
    }
    return render(request, 'admin_panel/feedback/feedback_list.html', context)


@admin_required
def feedback_update_status(request, pk):
    """
    Updates status and internal resolution notes for a CustomerFeedback record.
    Requires staff/admin authorization (@admin_required).
    """
    from core.models import CustomerFeedback
    feedback_obj = get_object_or_404(CustomerFeedback, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip().upper()
        admin_notes = request.POST.get('admin_notes', '').strip()

        valid_statuses = [choice[0] for choice in CustomerFeedback.STATUS_CHOICES]

        if new_status in valid_statuses:
            feedback_obj.status = new_status
            if admin_notes:
                feedback_obj.admin_notes = admin_notes
            feedback_obj.save()
            messages.success(request, f"Feedback from {feedback_obj.name} updated to '{feedback_obj.get_status_display()}'.")
        else:
            messages.error(request, "Invalid feedback status selected.")

    return redirect('admin_panel:feedback_list')



