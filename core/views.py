from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Avg, Count
from booking.models import ServiceCategory, Service
from .models import Review


def index(request):
    """
    Bolbash Beauty Spot Homepage view.
    Renders the primary landing page with core service showcases, academy introduction,
    shop previews, and approved customer reviews.
    """
    approved_reviews = Review.objects.filter(status=Review.STATUS_APPROVED).select_related('user', 'booking', 'service').order_by('-created_at')[:6]
    avg_rating_res = Review.objects.filter(status=Review.STATUS_APPROVED).aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_res, 1) if avg_rating_res else 5.0
    approved_count = Review.objects.filter(status=Review.STATUS_APPROVED).count()

    context = {
        'approved_reviews': approved_reviews,
        'avg_rating': avg_rating,
        'approved_count': approved_count,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    Bolbash Beauty Spot About Us view.
    Renders the brand story, service philosophy, craftsmanship standards, and location details.
    """
    return render(request, 'core/about.html')


def service_list(request):
    """
    Bolbash Beauty Spot Services Landing View.
    Fetches all active service categories and services for category filtering and display.
    """
    categories = ServiceCategory.objects.prefetch_related('services').all().order_by('display_order', 'id')
    featured_services = Service.objects.filter(active=True, featured=True).select_related('category').order_by('category__display_order', 'display_order', 'id')
    all_services = Service.objects.filter(active=True).select_related('category').order_by('category__display_order', 'display_order', 'id')

    context = {
        'categories': categories,
        'featured_services': featured_services,
        'services': all_services,
    }
    return render(request, 'core/service_list.html', context)


def service_detail(request, slug):
    """
    Bolbash Beauty Spot Service Detail View.
    Renders individual service overview, descriptions, expectations, related services,
    and approved customer ratings/reviews for this specific service.
    """
    service = get_object_or_404(Service, slug=slug, active=True)
    related_services = Service.objects.filter(
        category=service.category, active=True
    ).exclude(id=service.id)[:3]

    approved_reviews = service.reviews.filter(status=Review.STATUS_APPROVED).select_related('user', 'booking').order_by('-created_at')
    avg_rating_res = approved_reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_res, 1) if avg_rating_res else None
    review_count = approved_reviews.count()

    context = {
        'service': service,
        'related_services': related_services,
        'approved_reviews': approved_reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
    }
    return render(request, 'core/service_detail.html', context)


def reviews_showcase(request):
    """
    Public Customer Reviews Showcase View at /reviews/.
    Displays all approved client reviews with star rating filtering and summary scores.
    """
    approved_reviews = Review.objects.filter(status=Review.STATUS_APPROVED).select_related('user', 'booking', 'service').order_by('-created_at')

    # Optional rating filter
    rating_param = request.GET.get('rating', '').strip()
    if rating_param.isdigit():
        r_val = int(rating_param)
        if 1 <= r_val <= 5:
            approved_reviews = approved_reviews.filter(rating=r_val)

    all_approved = Review.objects.filter(status=Review.STATUS_APPROVED)
    total_count = all_approved.count()
    avg_rating_res = all_approved.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating_res, 1) if avg_rating_res else 5.0

    five_star_count = all_approved.filter(rating=5).count()
    four_star_count = all_approved.filter(rating=4).count()
    three_star_count = all_approved.filter(rating=3).count()

    context = {
        'reviews': approved_reviews,
        'total_count': total_count,
        'avg_rating': avg_rating,
        'five_star_count': five_star_count,
        'four_star_count': four_star_count,
        'three_star_count': three_star_count,
        'selected_rating': rating_param,
    }
    return render(request, 'core/reviews_showcase.html', context)



def custom_404(request, exception=None):
    """Custom 404 Page Not Found View Handler."""
    return render(request, '404.html', status=404)


def custom_403(request, exception=None):
    """Custom 403 Access Denied View Handler."""
    return render(request, '403.html', status=403)


def custom_500(request):
    """Custom 500 Server Error View Handler."""
    return render(request, '500.html', status=500)


def bridal(request):
    """
    Bolbash Beauty Spot Dedicated Bridal Experience View.
    Fetches bridal-focused services, displays luxury bridal gallery showcase,
    preparation timelines, testimonials, and consultation booking CTAs.
    """
    from django.db.models import Q
    bridal_services = Service.objects.filter(active=True).filter(
        Q(name__icontains='bridal') | 
        Q(name__icontains='bride') | 
        Q(name__icontains='wedding') | 
        Q(category__name__icontains='bridal')
    ).select_related('category')

    # Fallback to general active services if specific bridal filter returns empty
    if not bridal_services.exists():
        bridal_services = Service.objects.filter(active=True).select_related('category')[:4]

    context = {
        'bridal_services': bridal_services,
    }
    return render(request, 'core/bridal.html', context)


def gallery(request):
    """
    Bolbash Beauty Spot Portfolio Gallery View.
    Renders visual showcase of salon craftsmanship across bridal styling,
    wig melts, transformations, natural hair, and events with client-side filtering & lightbox.
    """
    from .models import GalleryImage
    gallery_images = GalleryImage.objects.filter(is_active=True).select_related('service_category').order_by('display_order', 'id')
    categories = GalleryImage.CATEGORY_CHOICES

    # Count of active images per category for empty state management
    category_counts = {}
    for cat_code, cat_label in categories:
        category_counts[cat_code] = gallery_images.filter(category=cat_code).count()

    context = {
        'gallery_images': gallery_images,
        'categories': categories,
        'category_counts': category_counts,
        'total_images_count': gallery_images.count(),
    }
    return render(request, 'core/gallery.html', context)


def contact(request):
    """
    Bolbash Beauty Spot Contact View.
    Displays centralized business contact details, phone, WhatsApp CTA, interactive map,
    and processes customer enquiry contact form submissions with server-side validation.
    """
    from django.contrib import messages
    from django.core.validators import validate_email, ValidationError
    from .models import ContactSubmission

    if request.method == 'POST':
        # Honeypot Anti-Spam Check: If 'website_url' hidden field is filled, silently reject spam bot
        honeypot = request.POST.get('website_url', '').strip()
        if honeypot:
            messages.success(
                request,
                "Message Sent! Thank you for contacting Bolbash Beauty Spot. We will get back to you as soon as possible."
            )
            return render(request, 'core/contact.html', {'success_submission': True})

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        errors = []
        if not name:
            errors.append("Please provide your full name.")
        if not email:
            errors.append("Please provide your email address.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Please enter a valid email address.")
        if not subject:
            errors.append("Please select or enter a subject for your enquiry.")
        if not message_text:
            errors.append("Please enter your message text.")

        if errors:
            for err in errors:
                messages.error(request, err)
            context = {
                'form_data': request.POST,
            }
            return render(request, 'core/contact.html', context)

        # Create contact enquiry record
        submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text,
            status=ContactSubmission.STATUS_NEW,
        )

        messages.success(
            request,
            "Message Sent! Thank you for contacting Bolbash Beauty Spot. We will get back to you as soon as possible."
        )
        return render(request, 'core/contact.html', {'success_submission': True})

    return render(request, 'core/contact.html')


def feedback(request):
    """
    Public Customer Feedback Submission View at /feedback/.
    Allows website visitors and authenticated customers to submit suggestions or complaints.
    """
    from django.contrib import messages
    from .forms import CustomerFeedbackForm

    if request.method == 'POST':
        # Honeypot Anti-Spam Check
        honeypot = request.POST.get('website_url', '').strip()
        if honeypot:
            messages.success(
                request,
                "Thank you for submitting your feedback to Bolbash Beauty Spot! Our management team will review it carefully."
            )
            return render(request, 'core/feedback.html', {'success_submission': True})

        form = CustomerFeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            if request.user.is_authenticated:
                fb.user = request.user
            fb.save()

            messages.success(
                request,
                "Thank you for your feedback! Your message has been submitted to Bolbash Beauty Spot management."
            )
            return render(request, 'core/feedback.html', {'success_submission': True, 'form': CustomerFeedbackForm()})
        else:
            messages.error(request, "Please correct the errors below to submit your feedback.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['name'] = request.user.get_full_name() or request.user.username
            initial_data['email'] = request.user.email
            if hasattr(request.user, 'customer_profile') and request.user.customer_profile.phone_number:
                initial_data['phone'] = request.user.customer_profile.phone_number
        form = CustomerFeedbackForm(initial=initial_data)

    context = {
        'form': form,
    }
    return render(request, 'core/feedback.html', context)


def robots_txt(request):
    """
    Serves the robots.txt file for search engine crawlers.
    """
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /admin-portal/\n"
        "Disallow: /accounts/\n"
        "Disallow: /booking/lookup/\n"
        "Disallow: /payments/\n"
        "\n"
        f"Sitemap: {sitemap_url}\n"
    )
    return HttpResponse(content, content_type="text/plain")






