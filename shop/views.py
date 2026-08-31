from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from .models import ProductCategory, Product, ProductImage, Cart, CartItem, Order, OrderItem


def _get_or_create_cart(request):
    """
    Helper function resolving the active shopping cart for authenticated user or guest session.
    Merges guest session cart items into user cart upon login using preserved pre_login_session_key.
    """
    if not request.session.session_key:
        request.session.create()
    current_key = request.session.session_key

    if request.user.is_authenticated:
        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        # Retrieve any guest cart associated with current or pre-login session key
        pre_login_key = request.session.get('pre_login_session_key')
        keys_to_check = [current_key]
        if pre_login_key and pre_login_key not in keys_to_check:
            keys_to_check.append(pre_login_key)

        guest_carts = Cart.objects.filter(session_key__in=keys_to_check, user__isnull=True)
        for guest_cart in guest_carts:
            for guest_item in guest_cart.items.select_related('product').all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=guest_item.product,
                    defaults={'quantity': guest_item.quantity}
                )
                if not created:
                    user_item.quantity = min(guest_item.product.stock_quantity, user_item.quantity + guest_item.quantity)
                    user_item.save()
            guest_cart.delete()

        if 'pre_login_session_key' in request.session:
            del request.session['pre_login_session_key']

        return user_cart
    else:
        cart, _ = Cart.objects.get_or_create(session_key=current_key, user__isnull=True)
        request.session['pre_login_session_key'] = current_key
        return cart



def shop_landing(request):
    """
    Renders public Bolbash Shop landing page at /shop/.
    Displays shop hero, category cards, and full searchable/filterable product catalogue directly on the page.
    """
    categories = ProductCategory.objects.filter(active=True).prefetch_related('products')
    products = Product.objects.filter(is_active=True).select_related('category')

    selected_category = request.GET.get('category', '').strip()
    selected_price = request.GET.get('price', '').strip()
    in_stock_only = request.GET.get('in_stock', '').strip()
    search_query = request.GET.get('q', '').strip()

    if selected_category:
        products = products.filter(category__slug=selected_category)

    if in_stock_only == 'true':
        products = products.filter(stock_quantity__gt=0)

    if selected_price == 'under_10k':
        products = products.filter(price__lt=10000)
    elif selected_price == '10k_25k':
        products = products.filter(price__gte=10000, price__lte=25000)
    elif selected_price == 'over_25k':
        products = products.filter(price__gt=25000)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query)
        )

    cart = _get_or_create_cart(request)

    context = {
        'categories': categories,
        'products': products,
        'total_products_count': Product.objects.filter(is_active=True).count(),
        'selected_category': selected_category,
        'selected_price': selected_price,
        'in_stock_only': in_stock_only,
        'search_query': search_query,
        'cart': cart,
    }
    return render(request, 'shop/shop_landing.html', context)


def product_catalogue(request):
    """
    Renders shop product catalogue at /shop/products/.
    Supports search query `q`, category filtering, price range filter, and stock availability toggle.
    """
    categories = ProductCategory.objects.filter(active=True)
    products = Product.objects.filter(is_active=True).select_related('category')

    selected_category = request.GET.get('category', '').strip()
    selected_price = request.GET.get('price', '').strip()
    in_stock_only = request.GET.get('in_stock', '').strip()
    search_query = request.GET.get('q', '').strip()

    if selected_category:
        products = products.filter(category__slug=selected_category)

    if in_stock_only == 'true':
        products = products.filter(stock_quantity__gt=0)

    if selected_price == 'under_10k':
        products = products.filter(price__lt=10000)
    elif selected_price == '10k_25k':
        products = products.filter(price__gte=10000, price__lte=25000)
    elif selected_price == 'over_25k':
        products = products.filter(price__gt=25000)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query)
        )

    cart = _get_or_create_cart(request)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_price': selected_price,
        'in_stock_only': in_stock_only,
        'search_query': search_query,
        'cart': cart,
        'total_products_count': Product.objects.filter(is_active=True).count(),
    }
    return render(request, 'shop/product_catalogue.html', context)


def product_detail(request, slug):
    """
    Renders individual product overview page at /shop/products/<slug>/.
    Displays image gallery thumbnails, stock indicator, quantity selector, add-to-cart form, and related products.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    gallery_images = product.gallery_images.all()

    # Fetch related products in same category (excluding current)
    related_products = list(Product.objects.filter(is_active=True, category=product.category).exclude(id=product.id).select_related('category')[:4])
    if len(related_products) < 4:
        needed = 4 - len(related_products)
        existing_ids = [p.id for p in related_products] + [product.id]
        additional_products = Product.objects.filter(is_active=True).exclude(id__in=existing_ids).select_related('category')[:needed]
        related_products.extend(list(additional_products))

    cart = _get_or_create_cart(request)

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'related_products': related_products,
        'cart': cart,
        'whatsapp_url': product.get_whatsapp_order_url(),
    }
    return render(request, 'shop/product_detail.html', context)


def cart_detail(request):
    """
    Renders shopping cart page at /shop/cart/.
    Displays cart line items, quantity modification controls, subtotal, and total.
    """
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__category').all()

    subtotal = cart.get_total_price()
    delivery_fee = Decimal('0.00')
    total_amount = subtotal

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
    }
    return render(request, 'shop/cart_detail.html', context)


def cart_add(request, product_id):
    """
    Handles POST requests to add a product to the cart.
    Validates active product, stock availability, and maximum inventory boundary.
    """
    if request.method != 'POST':
        return redirect('shop:product_catalogue')

    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        quantity = 1

    if not product.is_in_stock:
        messages.error(request, f"Sorry, '{product.name}' is currently out of stock.")
        return redirect('shop:product_detail', slug=product.slug)

    cart = _get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 0}
    )

    new_quantity = cart_item.quantity + quantity

    if new_quantity > product.stock_quantity:
        cart_item.quantity = product.stock_quantity
        cart_item.save()
        messages.warning(request, f"Quantity adjusted to available stock limit of {product.stock_quantity} for '{product.name}'.")
    else:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f"Added {quantity}x '{product.name}' to your shopping cart.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and 'cart' in next_url:
        return redirect('shop:cart_detail')

    return redirect('shop:cart_detail')


def cart_update(request, item_id):
    """
    Handles POST requests to update quantity for a specific cart line item.
    """
    if request.method != 'POST':
        return redirect('shop:cart_detail')

    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, f"Removed '{cart_item.product.name}' from your cart.")
        return redirect('shop:cart_detail')

    if quantity > cart_item.product.stock_quantity:
        cart_item.quantity = cart_item.product.stock_quantity
        cart_item.save()
        messages.warning(request, f"Maximum available stock for '{cart_item.product.name}' is {cart_item.product.stock_quantity}.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Updated quantity for '{cart_item.product.name}'.")

    return redirect('shop:cart_detail')


def cart_remove(request, item_id):
    """
    Handles POST requests to remove a line item from cart.
    """
    if request.method != 'POST':
        return redirect('shop:cart_detail')

    cart = _get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()

    messages.info(request, f"Removed '{product_name}' from your shopping cart.")
    return redirect('shop:cart_detail')


def checkout(request):
    """
    Handles checkout form rendering and POST order creation with Paystack payment initiation.
    Validates cart non-empty state, calculates authoritative amounts server-side, creates Order & Payment instances.
    """
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        messages.warning(request, "Your shopping cart is empty. Please add products before checking out.")
        return redirect('shop:product_catalogue')

    # Validate stock availability for all cart items
    out_of_stock_items = []
    for item in cart_items:
        if not item.product.is_active or item.product.stock_quantity < item.quantity:
            out_of_stock_items.append(f"{item.product.name} (Available: {item.product.stock_quantity})")

    if out_of_stock_items:
        messages.error(request, f"Stock restriction: Please adjust cart items: {', '.join(out_of_stock_items)}")
        return redirect('shop:cart_detail')

    subtotal = cart.get_total_price()
    delivery_fee = Decimal('0.00')
    total_amount = subtotal

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip().lower()
        customer_phone = request.POST.get('customer_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        city = request.POST.get('city', 'Ibadan').strip()
        state = request.POST.get('state', 'Oyo State').strip()
        delivery_notes = request.POST.get('delivery_notes', '').strip()

        if not customer_name or not customer_email or not customer_phone or not shipping_address:
            messages.error(request, "Please fill in all required delivery information fields.")
            return render(request, 'shop/checkout.html', {
                'cart': cart,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'total_amount': total_amount,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'shipping_address': shipping_address,
                'city': city,
                'state': state,
                'delivery_notes': delivery_notes,
            })

        # Atomic Order Creation & Itemization
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                shipping_address=shipping_address,
                city=city,
                state=state,
                delivery_notes=delivery_notes,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total_amount=total_amount,
                payment_status=Order.PAYMENT_UNPAID,
                order_status=Order.STATUS_PENDING
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name_snapshot=item.product.name,
                    product_price_snapshot=item.product.price,
                    quantity=item.quantity,
                    subtotal=item.get_subtotal()
                )

        # Initialize Paystack Payment Session
        from payments.models import Payment
        from payments.services import PaystackService

        amount_kobo = int(float(total_amount) * 100)

        payment = Payment.objects.create(
            order=order,
            amount=float(total_amount),
            currency='NGN',
            status=Payment.STATUS_PENDING,
            payment_type=Payment.PAYMENT_TYPE_ORDER
        )

        callback_url = request.build_absolute_uri(reverse('payments:verify_payment')) + f"?payment_ref={payment.reference}"

        try:
            res = PaystackService.initialize_transaction(
                email=customer_email,
                amount_kobo=amount_kobo,
                reference=payment.reference,
                callback_url=callback_url,
                metadata={
                    'order_number': order.order_number,
                    'payment_reference': payment.reference,
                    'customer_name': customer_name,
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
                return redirect('shop:order_confirmation', order_number=order.order_number)

        except Exception as e:
            payment.status = Payment.STATUS_FAILED
            payment.save()
            messages.error(request, f"Unable to initialize order payment: {str(e)}")
            return redirect('shop:order_confirmation', order_number=order.order_number)

    # Pre-fill user details if logged in
    initial_name = request.user.get_full_name() or request.user.username if request.user.is_authenticated else ''
    initial_email = request.user.email if request.user.is_authenticated else ''

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'customer_name': initial_name,
        'customer_email': initial_email,
    }
    return render(request, 'shop/checkout.html', context)


def order_confirmation(request, order_number):
    """
    Displays order receipt and confirmation page at /shop/orders/<order_number>/.
    """
    order = get_object_or_404(Order, order_number=order_number)
    order_items = order.items.select_related('product').all()

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'shop/order_confirmation.html', context)


@login_required(login_url='academy:login')
def customer_orders(request):
    """
    Displays order history list for authenticated customer at /shop/my-orders/.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items')

    context = {
        'orders': orders,
    }
    return render(request, 'shop/customer_orders.html', context)


@login_required(login_url='academy:login')
def customer_order_detail(request, order_number):
    """
    Displays detailed receipt for an individual order owned by authenticated customer.
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order_items = order.items.select_related('product').all()

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'shop/customer_order_detail.html', context)
