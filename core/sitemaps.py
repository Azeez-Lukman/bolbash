from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from booking.models import Service
from academy.models import Course
from shop.models import Product
from blog.models import BlogPost, BlogCategory


class StaticViewSitemap(Sitemap):
    """
    Sitemap class for static public landing pages.
    """
    changefreq = 'weekly'

    def items(self):
        return [
            'core:index',
            'core:about',
            'core:service_list',
            'core:bridal',
            'core:gallery',
            'blog:post_list',
            'core:reviews_showcase',
            'core:contact',
            'shop:shop_landing',
            'shop:product_catalogue',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item in ['core:index']:
            return 1.0
        elif item in ['core:service_list', 'core:bridal', 'blog:post_list', 'shop:shop_landing']:
            return 0.9
        return 0.8


class ServiceSitemap(Sitemap):
    """
    Sitemap class for individual salon services.
    """
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Service.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    """
    Sitemap class for published beauty editorial articles.
    """
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    """
    Sitemap class for blog categories.
    """
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return BlogCategory.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class CourseSitemap(Sitemap):
    """
    Sitemap class for individual beauty academy courses (preserved).
    """
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Course.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProductSitemap(Sitemap):
    """
    Sitemap class for individual shop products.
    """
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'blog': BlogSitemap,
    'blog_categories': BlogCategorySitemap,
    'courses': CourseSitemap,
    'products': ProductSitemap,
}
