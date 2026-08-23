import secrets
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone


class ProductCategory(models.Model):
    """
    Model representing product categories in the Bolbash online shop.
    (e.g., Hair Care, Skin Care, Beauty Tools, Accessories, Academy Materials)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Category description for customer guidance.")
    icon = models.CharField(max_length=50, blank=True, help_text="Optional emoji or icon identifier.")
    order = models.PositiveIntegerField(default=0, help_text="Display ordering weight.")
    active = models.BooleanField(default=True, help_text="Whether category is publicly visible.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Model representing a physical beauty product, hair maintenance item, or beauty tool.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    short_description = models.CharField(max_length=255, help_text="Short summary for product cards.")
    full_description = models.TextField(help_text="Detailed product specification and usage instructions.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Product price in NGN.")
    image = models.ImageField(upload_to='shop/products/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=10, help_text="Current available inventory stock.")
    is_active = models.BooleanField(default=True, help_text="Whether product is listed for sale.")
    is_featured = models.BooleanField(default=False, help_text="Whether to feature prominently on shop landing page.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.name} (NGN {self.price})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.is_active and self.stock_quantity > 0

    def get_whatsapp_order_url(self):
        """Generates dynamic WhatsApp enquiry/order link."""
        from urllib.parse import quote
        message = f"Hello Bolbash Beauty Spot, I am interested in purchasing '{self.name}' (NGN {self.price}). Is it available?"
        encoded = quote(message)
        return f"https://wa.me/message/UW6FRPKW3STAM1?text={encoded}"


class ProductImage(models.Model):
    """
    Additional product gallery images for product detail page.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='shop/products/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product Gallery Image"
        verbose_name_plural = "Product Gallery Images"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} Image {self.id}"


class Cart(models.Model):
    """
    Shopping Cart associated with authenticated user or guest session.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
        ordering = ['-updated_at']

    def __str__(self):
        owner = self.user.username if self.user else f"Guest ({self.session_key})"
        return f"Cart #{self.id} - {owner}"

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Individual product line item inside a shopping cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """
    Customer Order created during checkout. Stores customer shipping details and overall order status.
    """
    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    ORDER_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_PROCESSING, 'Processing Order'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_UNPAID = 'UNPAID'
    PAYMENT_PENDING = 'PENDING'
    PAYMENT_PAID = 'PAID'
    PAYMENT_FAILED = 'FAILED'
    PAYMENT_REFUNDED = 'REFUNDED'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_UNPAID, 'Unpaid'),
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
        (PAYMENT_REFUNDED, 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True, db_index=True, help_text="Unique reference e.g. BBS-ORD-YYYYMMDD-XXXX")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer Shipping Information
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100, default='Ibadan')
    state = models.CharField(max_length=100, default='Oyo State')
    delivery_notes = models.TextField(blank=True, help_text="Optional delivery instructions.")

    # Financial Summary
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status Fields
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_UNPAID)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=STATUS_PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shop Order"
        verbose_name_plural = "Shop Orders"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name} (NGN {self.total_amount})"

    @classmethod
    def generate_order_number(cls):
        """Generates unique order reference format BBS-ORD-YYYYMMDD-XXXX."""
        date_str = timezone.now().strftime("%Y%m%d")
        random_suffix = secrets.token_hex(2).upper()
        return f"BBS-ORD-{date_str}-{random_suffix}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            num = self.generate_order_number()
            while Order.objects.filter(order_number=num).exists():
                num = self.generate_order_number()
            self.order_number = num
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Line item inside a completed Order.
    Preserves historical product price and name at the moment of purchase.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name_snapshot = models.CharField(max_length=200)
    product_price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Line Item"
        verbose_name_plural = "Order Line Items"

    def __str__(self):
        return f"{self.quantity}x {self.product_name_snapshot} (Order #{self.order.order_number})"
