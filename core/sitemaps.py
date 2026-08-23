from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from booking.models import Service
from academy.models import Course
from shop.models import Product


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
            'core:reviews_showcase',
            'core:contact',
            'academy:academy_landing',
            'academy:course_list',
            'shop:shop_landing',
            'shop:product_catalogue',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item in ['core:index']:
            return 1.0
        elif item in ['core:service_list', 'core:bridal', 'academy:academy_landing', 'shop:shop_landing']:
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


class CourseSitemap(Sitemap):
    """
    Sitemap class for individual beauty academy courses.
    """
    changefreq = 'weekly'
    priority = 0.8

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
    'courses': CourseSitemap,
    'products': ProductSitemap,
}
