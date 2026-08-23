from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponse, Http404
from .models import CourseCategory, Course, StudentProfile, Enrollment, Module, Lesson, LessonProgress, Certificate




def academy_landing(request):
    """
    Renders the public-facing Bolbash Beauty Academy landing page.
    Displays training value proposition, target student groups, training areas,
    database-driven featured courses, and WhatsApp enquiry CTAs.
    """
    categories = CourseCategory.objects.filter(active=True).prefetch_related('courses')
    featured_courses = Course.objects.filter(active=True, featured=True).select_related('category')
    all_courses = Course.objects.filter(active=True).select_related('category')

    context = {
        'categories': categories,
        'featured_courses': featured_courses,
        'all_courses': all_courses,
    }
    return render(request, 'academy/academy_landing.html', context)


def course_list(request):
    """
    Renders the public Academy Course Catalogue page at /academy/courses/.
    Supports database-driven course display, category filtering, format filtering,
    search, and responsive empty states.
    """
    categories = CourseCategory.objects.filter(active=True)
    courses = Course.objects.filter(active=True).select_related('category')

    selected_category = request.GET.get('category', '').strip()
    selected_format = request.GET.get('format', '').strip()
    search_query = request.GET.get('q', '').strip()

    if selected_category:
        courses = courses.filter(category__slug=selected_category)

    if selected_format:
        courses = courses.filter(format_type=selected_format)

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query)
        )

    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': selected_category,
        'selected_format': selected_format,
        'search_query': search_query,
        'total_courses_count': Course.objects.filter(active=True).count(),
    }
    return render(request, 'academy/course_list.html', context)


def course_detail(request, slug):
    """
    Renders individual public course overview page at /academy/courses/<slug>/.
    Only active courses are publicly accessible; inactive courses return HTTP 404.
    Checks whether the authenticated student is already enrolled in this course.
    """
    course = get_object_or_404(Course, slug=slug, active=True)

    # Check student enrollment state if authenticated
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment:
            is_enrolled = True

    # Fetch related courses (same category preferred, excluding current course)
    related_courses = list(Course.objects.filter(active=True, category=course.category).exclude(id=course.id).select_related('category')[:3])
    if len(related_courses) < 3:
        needed = 3 - len(related_courses)
        existing_ids = [c.id for c in related_courses] + [course.id]
        additional_courses = Course.objects.filter(active=True).exclude(id__in=existing_ids).select_related('category')[:needed]
        related_courses.extend(list(additional_courses))

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'related_courses': related_courses,
        'learning_outcomes': course.get_learning_outcomes_list(),
        'target_audience': course.get_target_audience_list(),
        'prerequisites': course.get_prerequisites_list(),
        'whatsapp_url': course.get_whatsapp_enquiry_url(),
    }
    return render(request, 'academy/course_detail.html', context)


@login_required(login_url='academy:login')
def course_enroll(request, slug):
    """
    Handles POST course enrollment creation at /academy/courses/<slug>/enroll/.
    Requires authentication, validates active course, gets student identity from session,
    enforces database uniqueness, creates Enrollment record with STATUS_PENDING and PAYMENT_UNPAID,
    and redirects to enrollment confirmation.
    """
    course = get_object_or_404(Course, slug=slug, active=True)

    if request.method != 'POST':
        return redirect('academy:course_detail', slug=slug)

    # Database-level get_or_create to prevent duplicate student enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'enrollment_status': Enrollment.STATUS_PENDING,
            'payment_status': Enrollment.PAYMENT_UNPAID,
        }
    )

    if created:
        messages.success(request, f"You have successfully initiated enrollment in {course.title}.")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")

    return redirect('academy:enrollment_confirmation', slug=course.slug)


@login_required(login_url='academy:login')
def course_pay_initiate(request, slug):
    """
    Initializes a Paystack payment session for a student's course tuition fee.
    Validates enrollment, checks idempotency, determines price server-side,
    creates a Payment record, and redirects student to Paystack payment gateway.
    """
    from payments.models import Payment
    from payments.services import PaystackService
    from django.urls import reverse

    course = get_object_or_404(Course, slug=slug, active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    # Idempotency check: If already paid
    if enrollment.payment_status == Enrollment.PAYMENT_PAID or enrollment.enrollment_status == Enrollment.STATUS_ACTIVE:
        messages.info(request, f"Your tuition for {course.title} has already been paid and verified.")
        return redirect('academy:enrollment_confirmation', slug=course.slug)

    # Server-side amount calculation
    amount_val = float(course.price) if course.price else 50000.00
    amount_kobo = int(amount_val * 100)

    # Create Payment instance
    payment = Payment.objects.create(
        enrollment=enrollment,
        amount=amount_val,
        currency='NGN',
        status=Payment.STATUS_PENDING,
        payment_type=Payment.PAYMENT_TYPE_COURSE
    )

    callback_url = request.build_absolute_uri(reverse('payments:verify_payment')) + f"?payment_ref={payment.reference}"

    try:
        res = PaystackService.initialize_transaction(
            email=request.user.email,
            amount_kobo=amount_kobo,
            reference=payment.reference,
            callback_url=callback_url,
            metadata={
                'course_title': course.title,
                'course_slug': course.slug,
                'student_email': request.user.email,
                'payment_reference': payment.reference,
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
            return redirect('academy:enrollment_confirmation', slug=course.slug)

    except Exception as e:
        payment.status = Payment.STATUS_FAILED
        payment.save()
        messages.error(request, f"Unable to initialize tuition payment: {str(e)}")
        return redirect('academy:enrollment_confirmation', slug=course.slug)


@login_required(login_url='academy:login')
def enrollment_confirmation(request, slug):
    """
    Renders enrollment confirmation page at /academy/courses/<slug>/enrollment-confirmation/.
    Displays course name, student identity, enrollment status, and payment requirement notice.
    """
    course = get_object_or_404(Course, slug=slug, active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    context = {
        'course': course,
        'enrollment': enrollment,
    }
    return render(request, 'academy/enrollment_confirmation.html', context)


def student_register(request):
    """
    Handles Academy student registration at /academy/register/.
    Validates input, checks for duplicate email, enforces Django password validation,
    hashes passwords, creates User and StudentProfile, logs in student automatically,
    and redirects to intended course or student area.
    """
    if request.user.is_authenticated:
        return redirect('academy:my_learning')

    redirect_url = request.GET.get('next', '')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        post_next = request.POST.get('next', redirect_url)

        # Basic Required Validation
        if not first_name or not last_name or not email or not password or not confirm_password:
            messages.error(request, "Please fill in all required fields to register your student account.")
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Email Format Validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Duplicate Email & Username Check
        if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            messages.error(request, "An account with this email address already exists. Please log in or use a different email address.")
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Password Confirmation Match
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please verify your passwords and try again.")
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Django Password Validation
        try:
            dummy_user = User(username=email, email=email, first_name=first_name, last_name=last_name)
            validate_password(password, user=dummy_user)
        except ValidationError as err:
            for error_msg in err.messages:
                messages.error(request, error_msg)
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Create User with secure password hashing & IntegrityError safety catch
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Create 1-to-1 StudentProfile
            StudentProfile.objects.create(
                user=user,
                phone_number=phone_number
            )
        except IntegrityError:
            messages.error(request, "An account with this email address already exists. Please log in or use a different email address.")
            return render(request, 'academy/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone_number,
                'next': post_next,
            })

        # Automatic Login
        login(request, user)
        messages.success(request, f"Welcome to Bolbash Beauty Academy, {first_name}! Your student account has been created successfully.")

        if post_next and url_has_allowed_host_and_scheme(post_next, allowed_hosts={request.get_host()}):
            return redirect(post_next)

        return redirect('academy:my_learning')

    return render(request, 'academy/register.html', {'next': redirect_url})


def student_login(request):
    """
    Handles Academy student login at /academy/login/.
    Authenticates against Django's User system, prevents account enumeration on failure,
    and redirects upon success to intended course or student area.
    """
    if request.user.is_authenticated:
        return redirect('academy:my_learning')

    redirect_url = request.GET.get('next', '')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        post_next = request.POST.get('next', redirect_url)

        if not email or not password:
            messages.error(request, "Please enter both your email address and password.")
            return render(request, 'academy/login.html', {'email': email, 'next': post_next})

        # Lookup user by email or username
        user_obj = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()
        if user_obj is not None:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if post_next and url_has_allowed_host_and_scheme(post_next, allowed_hosts={request.get_host()}):
                    return redirect(post_next)
                return redirect('academy:my_learning')

        # Generic safe error message to prevent account enumeration
        messages.error(request, "Invalid login details. Please check your information and try again.")
        return render(request, 'academy/login.html', {'email': email, 'next': post_next})

    return render(request, 'academy/login.html', {'next': redirect_url})



def student_logout(request):
    """
    Handles secure student logout at /academy/logout/.
    Uses Django's logout functionality and redirects to Academy landing page.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out of your student account.")
    return redirect('academy:academy_landing')


@login_required(login_url='academy:login')
def my_learning(request):

    """
    Protected student area view at /academy/my-learning/.
    Displays student profile identity, summary stats (Total Enrolled, In Progress, Completed, Certificates),
    course progress percentage, progress status badges, and action buttons.
    """
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = list(request.user.enrollments.select_related('course', 'course__category').all())

    # Build student statistics
    in_progress_count = 0
    completed_count = 0

    for enrollment in enrollments:
        # Trigger server-side completion update check
        enrollment.check_and_update_completion()
        pct = enrollment.get_progress_percentage()
        if enrollment.enrollment_status == Enrollment.STATUS_COMPLETED:
            completed_count += 1
        elif pct > 0:
            in_progress_count += 1

    certificates_count = Certificate.objects.filter(user=request.user).count()

    context = {
        'student': request.user,
        'profile': profile,
        'enrollments': enrollments,
        'total_enrolled': len(enrollments),
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'certificates_count': certificates_count,
    }
    return render(request, 'academy/my_learning.html', context)


@login_required(login_url='academy:login')
def course_learn(request, slug):
    """
    Directs student to their next unfinished lesson for the course.
    Validates enrollment and payment status.
    """
    course = get_object_or_404(Course, slug=slug, active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    # Check payment boundary for paid courses
    if course.price and course.price > 0:
        if enrollment.payment_status != Enrollment.PAYMENT_PAID and enrollment.enrollment_status != Enrollment.STATUS_ACTIVE and enrollment.enrollment_status != Enrollment.STATUS_COMPLETED:
            messages.warning(request, f"Please complete your tuition fee payment to access the course content for {course.title}.")
            return redirect('academy:enrollment_confirmation', slug=course.slug)

    next_lesson = enrollment.get_next_unfinished_lesson()
    if not next_lesson:
        messages.info(request, f"No lessons available for {course.title} yet. Please check back soon.")
        return redirect('academy:my_learning')

    return redirect('academy:lesson_detail', course_slug=course.slug, lesson_slug=next_lesson.slug)


@login_required(login_url='academy:login')
def lesson_detail(request, course_slug, lesson_slug):
    """
    LMS Learning Player view rendering individual course lesson.
    Displays course curriculum sidebar with modules & lessons, lesson content,
    video tutorial (if present), completion status toggle, and prev/next navigation.
    """
    course = get_object_or_404(Course, slug=course_slug, active=True)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    # Check payment boundary
    if course.price and course.price > 0:
        if enrollment.payment_status != Enrollment.PAYMENT_PAID and enrollment.enrollment_status != Enrollment.STATUS_ACTIVE and enrollment.enrollment_status != Enrollment.STATUS_COMPLETED:
            messages.warning(request, f"Please complete tuition payment to access lessons for {course.title}.")
            return redirect('academy:enrollment_confirmation', slug=course.slug)

    modules = course.modules.prefetch_related('lessons').all()
    all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))

    current_lesson = get_object_or_404(Lesson, module__course=course, slug=lesson_slug)

    # Student progress set
    completed_lesson_ids = set(
        LessonProgress.objects.filter(user=request.user, lesson__module__course=course, completed=True)
        .values_list('lesson_id', flat=True)
    )

    is_completed = current_lesson.id in completed_lesson_ids

    # Navigation prev / next calculation
    current_index = -1
    for idx, lsn in enumerate(all_lessons):
        if lsn.id == current_lesson.id:
            current_index = idx
            break

    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index >= 0 and current_index < len(all_lessons) - 1 else None

    # Calculate current enrollment progress percentage
    progress_percentage = enrollment.get_progress_percentage()

    context = {
        'course': course,
        'enrollment': enrollment,
        'modules': modules,
        'current_lesson': current_lesson,
        'completed_lesson_ids': completed_lesson_ids,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'progress_percentage': progress_percentage,
        'certificate': getattr(enrollment, 'certificate', None),
    }
    return render(request, 'academy/lesson_detail.html', context)


@login_required(login_url='academy:login')
def lesson_toggle_complete(request, lesson_id):
    """
    Handles POST requests to mark a lesson complete or incomplete.
    Updates LessonProgress, recalculates course progress %, updates completion state,
    and auto-creates Certificate upon 100% completion.
    """
    if request.method != 'POST':
        return redirect('academy:my_learning')

    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )

    if not created:
        progress.completed = not progress.completed
        progress.save()

    # Recalculate enrollment progress & check course completion
    course_completed = enrollment.check_and_update_completion()

    if progress.completed:
        messages.success(request, f"Lesson '{lesson.title}' marked as completed! Keep going!")
        if course_completed:
            messages.success(request, f"🎉 Congratulations! You have completed all lessons in '{course.title}' and earned your Graduation Certificate!")
    else:
        messages.info(request, f"Lesson '{lesson.title}' marked as incomplete.")

    # Redirect to next lesson or current lesson
    if progress.completed:
        all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))
        current_idx = next((i for i, lsn in enumerate(all_lessons) if lsn.id == lesson.id), -1)
        if current_idx >= 0 and current_idx < len(all_lessons) - 1:
            next_lsn = all_lessons[current_idx + 1]
            return redirect('academy:lesson_detail', course_slug=course.slug, lesson_slug=next_lsn.slug)

    return redirect('academy:lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)


@login_required(login_url='academy:login')
def view_certificate(request, certificate_id):
    """
    Renders high-resolution, printable HTML Graduation Certificate.
    Accessible to certificate owner or staff.
    """
    cert = get_object_or_404(Certificate, certificate_id=certificate_id)

    # Permission check: must be owner or superuser
    if cert.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have authorization to view this certificate.")
        return redirect('academy:my_learning')

    context = {
        'certificate': cert,
        'student': cert.user,
        'course': cert.course,
        'issue_date': cert.issue_date,
        'verification_url': request.build_absolute_uri(f"/academy/verify-certificate/{cert.certificate_id}/"),
    }
    return render(request, 'academy/certificate_detail.html', context)


@login_required(login_url='academy:login')
def download_certificate_pdf(request, certificate_id):
    """
    Generates downloadable PDF certificate using ReportLab.
    """
    import io
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

    cert = get_object_or_404(Certificate, certificate_id=certificate_id)

    if cert.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access to certificate PDF.")
        return redirect('academy:my_learning')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Draw Border & Branding
    p.setStrokeColor(colors.HexColor('#DB2777'))  # Bolbash Pink
    p.setLineWidth(4)
    p.rect(20, 20, width - 40, height - 40)

    p.setStrokeColor(colors.HexColor('#0F172A'))  # Dark Accent
    p.setLineWidth(1)
    p.rect(26, 26, width - 52, height - 52)

    # Header
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.HexColor('#0F172A'))
    p.drawCentredString(width / 2, height - 80, "BOLBASH BEAUTY ACADEMY")

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor('#DB2777'))
    p.drawCentredString(width / 2, height - 100, "IBADAN, NIGERIA • CERTIFICATE OF COMPLETION")

    # Statement
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2, height - 160, "This is to certify that")

    # Student Name
    student_name = cert.user.get_full_name() or cert.user.username
    p.setFont("Helvetica-Bold", 26)
    p.setFillColor(colors.HexColor('#0F172A'))
    p.drawCentredString(width / 2, height - 205, student_name.upper())

    p.setStrokeColor(colors.HexColor('#DB2777'))
    p.setLineWidth(2)
    p.line(width / 2 - 180, height - 215, width / 2 + 180, height - 215)

    # Course Completion Statement
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2, height - 250, "has successfully completed all requirements and modules for")

    # Course Name
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.HexColor('#DB2777'))
    p.drawCentredString(width / 2, height - 285, cert.course.title)

    # Details Footer
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor('#64748B'))
    p.drawString(60, 80, f"Date Issued: {cert.issue_date.strftime('%B %d, %Y')}")
    p.drawRightString(width - 60, 80, f"Certificate ID: {cert.certificate_id}")

    p.drawCentredString(width / 2, 50, "Verified Official Certificate • Bolbash Beauty Academy")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bolbash_Certificate_{cert.certificate_id}.pdf"'
    return response


def verify_certificate(request, certificate_id=None):
    """
    Public Certificate Verification view at /academy/verify-certificate/
    or /academy/verify-certificate/<certificate_id>/.
    Validates certificate ID authenticity and displays graduation details.
    """
    query_id = certificate_id or request.GET.get('id', '').strip()
    cert = None
    searched = False
    invalid = False

    if query_id:
        searched = True
        cert = Certificate.objects.filter(certificate_id__iexact=query_id).select_related('user', 'course').first()
        if not cert:
            invalid = True

    context = {
        'query_id': query_id,
        'certificate': cert,
        'searched': searched,
        'invalid': invalid,
    }
    return render(request, 'academy/verify_certificate.html', context)


@login_required(login_url='academy:login')
def my_learning_legacy(request):
    return my_learning(request)

