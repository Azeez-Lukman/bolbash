from django.contrib import admin
from .models import ProductCategory, Product, ProductImage, Cart, CartItem, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name_snapshot', 'product_price_snapshot', 'quantity', 'subtotal')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'active', 'created_at')
    list_editable = ('order', 'active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock_quantity', 'is_active', 'is_featured')
    inlines = [ProductImageInline]
    ordering = ('-is_featured', '-created_at')

    fieldsets = (
        ('Product Overview', {
            'fields': ('name', 'slug', 'category', 'short_description', 'full_description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Product Media', {
            'fields': ('image',)
        }),
        ('Publishing & Visibility', {
            'fields': ('is_active', 'is_featured')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'customer_email', 'total_amount', 'payment_status', 'order_status', 'created_at')
    list_filter = ('payment_status', 'order_status', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_email', 'customer_phone', 'city')
    readonly_fields = ('order_number', 'subtotal', 'delivery_fee', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    list_editable = ('order_status', 'payment_status')
    ordering = ('-created_at',)

    fieldsets = (
        ('Order Reference', {
            'fields': ('order_number', 'user', 'order_status', 'payment_status')
        }),
        ('Customer & Delivery Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'shipping_address', 'city', 'state', 'delivery_notes')
        }),
        ('Financial Summary', {
            'fields': ('subtotal', 'delivery_fee', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_total_items_count', 'get_total_price', 'updated_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    inlines = [CartItemInline]
