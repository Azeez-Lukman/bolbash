from django.contrib import admin
from django.utils import timezone
from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Articles'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'reading_time_minutes', 'published_at', 'views_count']
    list_filter = ['status', 'is_featured', 'category', 'published_at', 'created_at']
    search_fields = ['title', 'excerpt', 'content', 'meta_title', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = []
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    ordering = ['-published_at', '-created_at']
    
    fieldsets = (
        ('Article Details', {
            'fields': ('title', 'slug', 'category', 'author', 'featured_image', 'excerpt', 'content')
        }),
        ('Publication & Visibility', {
            'fields': ('status', 'is_featured', 'reading_time_minutes', 'published_at', 'views_count')
        }),
        ('SEO & Search Metadata', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description', 'canonical_url'),
            'description': 'Search engine metadata for Google indexing and Open Graph sharing.'
        }),
    )

    readonly_fields = ['views_count']
    actions = ['publish_posts', 'unpublish_posts', 'mark_as_featured']

    @admin.action(description='Publish selected articles')
    def publish_posts(self, request, queryset):
        count = queryset.update(status=BlogPost.STATUS_PUBLISHED, published_at=timezone.now())
        self.message_user(request, f"{count} article(s) successfully published.")

    @admin.action(description='Revert selected articles to Draft')
    def unpublish_posts(self, request, queryset):
        count = queryset.update(status=BlogPost.STATUS_DRAFT)
        self.message_user(request, f"{count} article(s) set to Draft.")

    @admin.action(description='Toggle selected articles as Featured')
    def mark_as_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} article(s) marked as featured.")
