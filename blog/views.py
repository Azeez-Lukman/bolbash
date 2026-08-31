from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F
from django.utils import timezone
from .models import BlogCategory, BlogPost


def post_list(request):
    """
    Editorial blog landing page displaying featured spotlight, category filters,
    keyword search, and paginated article grid.
    """
    search_query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    posts = BlogPost.objects.published()

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=selected_category)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Featured Post for hero spotlight (only if not searching or filtering)
    featured_post = None
    if not search_query and not category_slug:
        featured_post = BlogPost.objects.published().filter(is_featured=True).first()
        if not featured_post:
            featured_post = BlogPost.objects.published().first()
        
        # Exclude featured post from the main listing if present
        if featured_post:
            posts = posts.exclude(pk=featured_post.pk)

    # Pagination: 6 articles per page
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    categories = BlogCategory.objects.all()

    context = {
        'featured_post': featured_post,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'total_posts_count': paginator.count,
    }
    return render(request, 'blog/post_list.html', context)


def category_detail(request, slug):
    """
    Filtered blog article list by specific category slug.
    """
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.published().filter(category=category)

    search_query = request.GET.get('q', '').strip()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    categories = BlogCategory.objects.all()

    context = {
        'selected_category': category,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': categories,
        'search_query': search_query,
        'total_posts_count': paginator.count,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """
    Luxury editorial article detail view with rich typography, author card,
    view count tracking, social sharing, and related articles.
    """
    # Allow staff members to preview drafts
    if request.user.is_staff:
        post = get_object_or_404(BlogPost.objects.select_related('category', 'author'), slug=slug)
    else:
        post = get_object_or_404(BlogPost.objects.published(), slug=slug)

    # Atomic increment of view counter
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.refresh_from_db(fields=['views_count'])

    # Related articles in same category
    related_posts = BlogPost.objects.published().filter(
        category=post.category
    ).exclude(pk=post.pk).order_by('-published_at')[:3]

    # Recent articles fallback if few related
    if related_posts.count() < 3:
        needed = 3 - related_posts.count()
        additional_posts = BlogPost.objects.published().exclude(
            pk__in=[post.pk] + [p.pk for p in related_posts]
        ).order_by('-published_at')[:needed]
        related_posts = list(related_posts) + list(additional_posts)

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)
