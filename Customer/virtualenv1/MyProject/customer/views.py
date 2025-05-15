from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import RegistrationForm, LoginForm, ProductForm
from .models import Product, Order, OrderItem, Cart
from django.db.models import Sum 
import datetime
from django.db.models.functions import TruncDay, TruncWeek
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
import json
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from .forms import BulkUploadForm

User = get_user_model()

# Show index page
def index(request):
    return render(request, 'index.html')

# Register a new user using the form
def register_customer(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the user (this will automatically hash the password and set the user_type)
            user = form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, "There were errors in your registration form.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

# Log in an existing user using the form

def login_customer(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username}!")
                
                # Redirect based on user type
                if user.user_type == 3:  # Admin
                    return redirect('dashboard')  # Redirect to the admin dashboard
                elif user.user_type == 1:  # Customer
                    return redirect('product_list')
                elif user.user_type == 2:  # Seller
                    return redirect('seller_dashboard')  # Redirect to the seller dashboard (if you have this view)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Show dashboard (only for authenticated users)
import json
from decimal import Decimal

import json
from decimal import Decimal

def dashboard_customer(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to access the dashboard.")
        return redirect('login')

    today = datetime.date.today()

    total_products = Product.objects.count()
    total_customers = User.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(sum=Sum('total'))['sum'] or 0
    categories = Category.objects.all()
    recent_orders = Order.objects.order_by('-created_at')[:5]
    products = Product.objects.all()
    bulk_form = BulkUploadForm()

    # Revenue this week (by day)
    week_revenue = (
        Order.objects
            .filter(created_at__week=today.isocalendar()[1])
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total=Sum('total'))
            .order_by('day')
    )

    # Revenue this month (by week)
    month_revenue = (
        Order.objects
            .filter(created_at__month=today.month)
            .annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(total=Sum('total'))
            .order_by('week')
    )

    # Top-selling products
    top_products = (
        OrderItem.objects
            .values('product__name')
            .annotate(sold=Sum('quantity'))
            .order_by('-sold')[:5]
    )

    low_stock_products = Product.objects.filter(stock__lt=5)

    # Convert Decimal values to float for JSON serialization
    revenue_labels = [entry['day'].strftime('%a') for entry in week_revenue]
    revenue_data = [float(entry['total']) if isinstance(entry['total'], Decimal) else entry['total'] for entry in week_revenue]

    context = {
        'user': request.user,
        'total_products': total_products,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'products': products,
        'categories': categories,
        'bulk_form': bulk_form,  
        'cart_items_count': Cart.objects.filter(user=request.user).count(),
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'top_products': top_products,
        'low_stock_products': low_stock_products,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
    }

    return render(request, 'dashboard.html', context)



# Log out the user
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Add new product (admin access assumed, using form)
def add_item(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect("dashboard")
        else:
            messages.error(request, "There was an error adding the product.")
    else:
        form = ProductForm()

    return render(request, "add.html", {'form': form})

# Edit product view
def edit_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "There was an error updating the product.")
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit.html', {'form': form, 'product': product})

# Delete product view
def delete_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('dashboard')

    return render(request, 'delete_product.html', {'product': product})

# Profile view
def profile(request):
    return render(request, "profile.html")

# Cart view
def Acart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'Admincart.html')

# Notifications view
def notifications(request):
    return render(request, 'notifications.html')

# Order detail view
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem  # adjust if in different app
from django.shortcuts import get_object_or_404

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
    })


# Edit order view
def edit_order(request, order_id):  
    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    if request.method == 'POST':
        # Handle form submission to edit order details (left for you to implement)
        pass

    return render(request, 'edit_order.html', {
        'order': order,
        'order_items': order_items,
    })  

# Customer list view (for staff only)
def customer_list(request):
    customers = User.objects.filter(is_superuser=False).order_by('-date_joined')  # Exclude admin
    return render(request, 'customer_list.html', {'customers': customers})

@user_passes_test(lambda u: u.is_staff)
def toggle_customer_status(request, user_id):
    customer = get_object_or_404(User, pk=user_id)
    customer.is_active = not customer.is_active
    customer.save()
    messages.success(request, f"Customer {'activated' if customer.is_active else 'blocked'} successfully.")
    return redirect('customer_list')

# Admin orders view
def admin_orders(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    orders = Order.objects.select_related('user').all()

    # Apply search
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query)
        )

    # Apply filter by status
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Paginate
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'orders.html', context, status=200)

# Admin products view
def admin_products(request):
    search_query = request.GET.get('search', '')
    stock_filter = request.GET.get('stock', '')
    products = Product.objects.all()

    # Apply search by product name or category
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Apply filter by stock status
    if stock_filter == 'low':
        products = products.filter(stock__lte=10, stock__gt=0)
    elif stock_filter == 'out':
        products = products.filter(stock__lte=0)
    elif stock_filter == 'in':
        products = products.filter(stock__gt=10)

    # Paginate
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'search_query': search_query,
        'stock_filter': stock_filter,
    }
    return render(request, 'products.html', context)

# Export inventory to CSV
import csv
from django.http import HttpResponse

def export_products_csv(request):
    """Download a CSV of all products."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=products.csv'
    writer = csv.writer(response)
    writer.writerow(['ID','Name','Category','Price','Offer','Stock'])
    for p in Product.objects.select_related('category').all():
        writer.writerow([
            p.id,
            p.name,
            p.category.name if p.category else '',
            f"{p.price:.2f}",
            p.offer or '',
            p.stock,
        ])
    return response

import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category
from django.core.files.base import ContentFile
import requests

def bulk_upload_products(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            category, _ = Category.objects.get_or_create(name=row['category'])

            product = Product(
                name=row['name'],
                category=category,
                price=float(row['price']),
                discount=float(row['discount']),
                stock=int(row['stock'])
            )

            # Fetch image from URL if provided
            if row.get('image_url'):
                try:
                    response = requests.get(row['image_url'])
                    if response.status_code == 200:
                        file_name = row['name'].replace(" ", "_") + '.jpg'
                        product.image.save(file_name, ContentFile(response.content), save=False)
                except Exception as e:
                    print("Image fetch failed:", e)

            product.save()

        messages.success(request, "Products uploaded successfully!")
        return redirect('dashboard')  # change as per your dashboard route

    messages.error(request, "CSV file required.")
    return redirect('dashboard')

from django.views.decorators.csrf import csrf_protect

@csrf_protect
def delete_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.image:
        product.image.delete(save=True)
        messages.success(request, "Product image deleted successfully.")
    return redirect('dashboard')


from django.contrib import messages
from .models import Product, Category

# ----------------------------
# IMAGE MANAGER
# ----------------------------
from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse

def image_manager(request):
    if request.method == 'POST':
        if 'upload' in request.POST:
            prod = get_object_or_404(Product, pk=request.POST['product_id'])
            img = request.FILES.get('image')
            if img:
                prod.image = img
                prod.save()
                messages.success(request, f"Image set for {prod.name}")

        elif 'delete' in request.POST:
            prod = get_object_or_404(Product, pk=request.POST['delete'])
            if prod.image:
                prod.image.delete(save=True)
                messages.info(request, f"Image removed for {prod.name}")

        # Redirect to dashboard and reopen modal
        return redirect(f"{reverse('dashboard')}?openImageModal=1")

    return redirect('dashboard')


# ----------------------------
# CATEGORY MANAGEMENT
# ----------------------------
def manage_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, f"Category '{name}' added.")
    return redirect('dashboard')


def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, f"Category renamed to '{new_name}'")
            return redirect('dashboard')
    return render(request, 'edit_category.html', {'category': category})



def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.warning(request, f"Category '{category.name}' deleted.")
    return redirect('dashboard')




from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Update the order status
        new_status = request.POST.get('status')
        if new_status and new_status != order.status:
            order.status = new_status
            order.save()

            # Send email notification if the status is updated
            send_order_status_email(order)

            # Redirect to orders list or success page
            return redirect('orders')  # Or specify another URL

    context = {'order': order}
    return render(request, 'edit_orders.html', context)


def send_order_status_email(order):
    """ Sends an email to the customer when the order status is updated. """
    subject = f"Your Order #{order.id} Status Updated"
    message = f"Hello {order.user.username},\n\n" \
              f"Your order #{order.id} status has been updated to {order.get_status_display()}.\n\n" \
              f"Thank you for shopping with us!"
    from_email = settings.DEFAULT_FROM_EMAIL  # Or specify your email here

    send_mail(subject, message, from_email, [order.user.email])

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order

def process_return_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        return_requested = request.POST.get('return_requested') == 'on'
        return_reason = request.POST.get('return_reason', '')
        refund_status = request.POST.get('refund_status')

        # Update order
        order.return_requested = return_requested
        order.return_reason = return_reason
        order.refund_status = refund_status

        if return_requested:
            order.status = 'R'  # Mark as Returned

        order.save()

        # Send email
        send_return_refund_email(order)

        return redirect('order_detail', order_id=order.id)

    return render(request, 'process_return_refund.html', {'order': order})


def send_return_refund_email(order):
    subject = f"Return/Refund Update for Order #{order.id}"
    html_message = render_to_string('emails/return_refund_notification.html', {'order': order})
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'Shop Admin <kalyanikhanavkar27@gmail.com>',
        [order.user.email],
        html_message=html_message,
    )

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import io

def generate_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    template_path = 'invoice.html'
    context = {'order': order}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order_id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        io.StringIO(html), dest=response
    )

    if pisa_status.err:
        return HttpResponse('We had errors while generating the PDF <pre>' + html + '</pre>')
    return response


# admin/views.py
from django.shortcuts import render
from django.http import JsonResponse

from customer.models import User,Product ,Order
from django.db.models import Sum, Count
import datetime

def analytics_dashboard(request):
    
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0  
    total_orders = Order.objects.count()
    total_customers = User.objects.count()

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
    }
    return render(request, 'analytics_dashboard.html', context)

from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from .models import Order, Product

def chart_data(request):
    # Total revenue
    total_revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0

    # Total orders and customers
    total_orders = Order.objects.count()
    total_customers = Order.objects.values('user').distinct().count()

    # Weekly revenue trend (last 4 weeks)
    weekly_labels = []
    weekly_data = []

    for i in range(4):
        start = now() - timedelta(weeks=i+1)
        end = now() - timedelta(weeks=i)
        label = f"Week {4 - i}"
        revenue = Order.objects.filter(created_at__range=(start, end)).aggregate(total=Sum('total'))['total'] or 0
        weekly_labels.append(label)
        weekly_data.append(revenue)

    # Reverse to get oldest to newest
    weekly_labels.reverse()
    weekly_data.reverse()

    # Monthly revenue trend (last 6 months)
    from django.db.models.functions import TruncMonth
    from django.utils.timezone import datetime
    import calendar

    six_months_ago = now() - timedelta(days=180)
    monthly_orders = (
        Order.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )
    monthly_labels = [calendar.month_name[entry['month'].month] for entry in monthly_orders]
    monthly_data = [entry['total'] for entry in monthly_orders]

    # Sales by category
    ''''
    from django.db.models import F
    category_data = (
        Product.objects.values('category')
        .annotate(total_sales=Count('order__id'))
    )
    
    '''

    # Top-selling products
    top_products = (
        Product.objects.annotate(order_count=Count('orderitem__order'))
        .order_by('-order_count')[:5]
    )
    top_products_data = [{'name': p.name, 'orders': p.order_count} for p in top_products]

    # Customer growth (monthly - dummy)
    customer_labels = ['Jan', 'Feb', 'Mar', 'Apr']
    customer_data = [120, 140, 180, 220]  # Replace with real data if available

    return JsonResponse({
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'revenue_labels': weekly_labels,
        'revenue_data': weekly_data,
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
       
        'top_products': top_products_data,
        'customer_labels': customer_labels,
        'customer_data': customer_data,
    })




#------------customer user views -----------------

from django.shortcuts import render
from .models import Product, Category ,Cart

def product_list(request):
    # Get all products, initially
    products = Product.objects.all()

    # Apply filters if provided in request
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__name=category_filter)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min and price_max:
        products = products.filter(price__gte=price_min, price__lte=price_max)

    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.all()  # Get all categories for filtering
 # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products': products_page,
        'categories': categories,
        'search_query': request.GET.get('q', ''),
        'min_price': request.GET.get('min_price', ''),
        'max_price': request.GET.get('max_price', ''),
        'min_discount': request.GET.get('min_discount', ''),
    }

    return render(request, 'customer/product_list.html', context)


def product_detail(request, product_id):
    # Fetch the product by its ID, or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)

    context = {
        'product': product,
    }
    
    return render(request, 'customer/product_detail.html', context)
# views.py
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Product


# views.py

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Retrieve or create a cart, but ensure that only one cart per user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Ensure cart is unique before proceeding
    if not created:
        cart = Cart.objects.get(user=request.user)  # fetch the existing cart

    item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        # If the item is already in the cart, increase the quantity
        item.quantity += 1
        item.save()

    messages.success(request, f"Added {product.name} to your cart.")
    return redirect('cart')


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    return render(request, 'customer/cart.html', {
        'cart': cart,
        'items': items
    })

@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', item.quantity))
        if quantity > 0:
            item.quantity = quantity
            item.save()
            messages.success(request, "Cart updated.")
        else:
            item.delete()
            messages.success(request, "Item removed from cart.")
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO

from .models import Cart, Order, OrderItem

def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # Calculate total
        total = sum(item.subtotal for item in cart_items)

        # Create Order
        order = Order.objects.create(user=request.user, total=total)

        # Create OrderItems and reduce stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        cart_items.delete()

        # Prepare items with totals
        items_with_total = []
        for item in order.items.all():
            items_with_total.append({
                'product': item.product,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.quantity * item.price
            })

        # Render PDF invoice
        pdf_context = {
            'user': request.user,
            'order': order,
            'items': items_with_total,
        }
        pdf_html = render_to_string('invoices/invoice.html', pdf_context)
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(pdf_html, dest=pdf_file)

        # Prepare and send email
        subject = f"Order Confirmation - #{order.id}"
        html_message = render_to_string('emails/order_confirmation.html', pdf_context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email]

        email = EmailMessage(subject, plain_message, from_email, recipient_list)
        email.content_subtype = "html"
        email.attach(f'invoice_order_{order.id}.pdf', pdf_file.getvalue(), 'application/pdf')
        email.send()

        messages.success(request, f"Order #{order.id} placed successfully! Confirmation and invoice emailed.")
        return redirect('my_orders')  # Redirect to order history

    return render(request, 'customer/checkout.html', {'cart': cart, 'items': cart_items})



def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'customer/order_summary.html', {'order': order})
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'customer/my_orders.html', {'orders': orders})

from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation(user_email, order_id):
    subject = f"Order Confirmation - #{order_id}"
    message = f"Dear Customer,\n\nThank you for your order #{order_id}!\nWe will notify you once it's shipped."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)

    print("Order confirmation email sent to:", user_email)
    
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    items_with_total = []
    for item in order.items.all():
        items_with_total.append({
            'product': item.product,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.quantity * item.price
        })

    context = {
        'user': request.user,
        'order': order,
        'items': items_with_total,
    }

    html = render_to_string('invoices/invoice.html', context)
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_order_{order.id}.pdf'
    return response