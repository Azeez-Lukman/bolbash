import math
import re
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone


class BlogCategory(models.Model):
    """
    Categorization for beauty editorial articles (e.g., Hair Care, Wig Maintenance, Bridal Prep).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True, help_text="Short description of this beauty category.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    @property
    def published_posts_count(self):
        return self.posts.filter(status=BlogPost.STATUS_PUBLISHED, published_at__lte=timezone.now()).count()


class BlogPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=BlogPost.STATUS_PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('category', 'author')

    def featured(self):
        return self.published().filter(is_featured=True)

    def recent(self):
        return self.published().order_by('-published_at')


class BlogPost(models.Model):
    """
    Editorial and SEO article model for Bolbash Beauty Spot.
    """
    STATUS_DRAFT = 'DRAFT'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    category = models.ForeignKey(
        BlogCategory, 
        on_delete=models.PROTECT, 
        related_name='posts',
        help_text="Primary category for this article."
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='blog_posts',
        help_text="Author of the article (defaults to staff user)."
    )
    featured_image = models.ImageField(
        upload_to='blog/covers/',
        blank=True,
        null=True,
        help_text="High-resolution editorial cover image."
    )
    excerpt = models.TextField(
        max_length=500,
        help_text="Short teaser summary for listing cards, hero banners, and search previews."
    )
    content = models.TextField(
        help_text="Full article body content with rich formatting."
    )

    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default=STATUS_DRAFT, 
        db_index=True
    )
    is_featured = models.BooleanField(
        default=False, 
        db_index=True,
        help_text="Highlight as a featured editorial story on the blog homepage."
    )
    reading_time_minutes = models.PositiveIntegerField(
        default=3, 
        help_text="Estimated read time in minutes (auto-calculated if left blank)."
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Total page views."
    )
    published_at = models.DateTimeField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="Publication timestamp. Posts with future dates will remain scheduled."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO Metadata
    meta_title = models.CharField(
        max_length=160, 
        blank=True, 
        help_text="Custom SEO title tag (optional - defaults to article title)."
    )
    meta_description = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Custom search engine meta description (optional - defaults to excerpt)."
    )
    canonical_url = models.URLField(
        blank=True, 
        help_text="Optional canonical override URL."
    )

    objects = BlogPostQuerySet.as_manager()

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Auto-set publication timestamp when status is set to PUBLISHED
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        # Auto-calculate reading time based on word count (~200 words per min)
        if self.content:
            clean_text = re.sub(r'<[^>]*>', ' ', self.content)
            word_count = len(clean_text.split())
            calculated_time = max(1, math.ceil(word_count / 200))
            if not self.reading_time_minutes or self.reading_time_minutes == 3:
                self.reading_time_minutes = calculated_time

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == self.STATUS_PUBLISHED and self.published_at and self.published_at <= timezone.now()

    @property
    def author_name(self):
        if self.author:
            full_name = self.author.get_full_name().strip()
            if full_name and not any(bad in full_name.lower() for bad in ['test', 'admin']):
                return full_name
            username = self.author.username.lower()
            if not any(bad in username for bad in ['admin', 'test', 'root', 'user']):
                return self.author.username
        return "Bolbash Hair Specialists"

    @property
    def seo_title(self):
        return self.meta_title if self.meta_title else self.title

    @property
    def seo_description(self):
        return self.meta_description if self.meta_description else self.excerpt
