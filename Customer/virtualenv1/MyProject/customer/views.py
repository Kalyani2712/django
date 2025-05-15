from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import RegistrationForm, LoginForm, ProductForm
from .models import Product, Category, Order, OrderItem, Cart
from django.db.models import Sum
import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import user_passes_test

# Show index page
def index(request):
    return render(request, 'index.html')

# Register a new user using the form
def register_customer(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
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
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Show dashboard (only for authenticated users)
# Corrected  Admin dashboard viewfrom django.db.models.functions import TruncDay, TruncMonth
from collections import defaultdict

def dashboard_customer(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to access the dashboard.")
        return redirect('login')

    today = datetime.date.today()
    last_7_days = today - datetime.timedelta(days=6)
    last_30_days = today - datetime.timedelta(days=30)

    total_products = Product.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(sum=Sum('total'))['sum'] or 0
    total_customers = User.objects.count()

    # Weekly/Monthly revenue for filters
    weekly_revenue = Order.objects.filter(created_at__date__gte=last_7_days).aggregate(sum=Sum('total'))['sum'] or 0
    monthly_revenue = Order.objects.filter(created_at__date__gte=last_30_days).aggregate(sum=Sum('total'))['sum'] or 0

    # Revenue Chart Data (last 7 days)
    chart_data = (
        Order.objects.filter(created_at__date__gte=last_7_days)
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(revenue=Sum('total'))
        .order_by('day')
    )

    # Top selling products
    top_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    # Recent logs (dummy - extend with your own activity logs model)
    system_logs = [
        {'timestamp': '2025-05-12 11:20', 'event': 'Admin logged in'},
        {'timestamp': '2025-05-12 11:25', 'event': 'New product added'},
        {'timestamp': '2025-05-12 11:30', 'event': 'Order placed by user X'}
    ]

    recent_orders = Order.objects.order_by('-created_at')[:5]
    products = Product.objects.all()

    return render(request, 'dashboard.html', {
        'total_products': total_products,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'total_customers': total_customers,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
        'products': products,
        'top_products': top_products,
        'system_logs': system_logs,
        'chart_data': chart_data,
        'cart_items_count': Cart.objects.filter(user=request.user).count(),
    })
# Show product list (for authenticated users)

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

# Optional edit view

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
def delete_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('dashboard')

    return render(request, 'delete_product.html', {'product': product})


def profile(request):
    return render(request, "profile.html")

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def notifications(request):
    return render(request, 'notifications.html')

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items,
    })

def edit_order(request, order_id):  
    if not request.user.is_authenticated:
        return redirect('login')

    order = Order.objects.get(id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    if request.method == 'POST':
        # Handle form submission to edit order details
        # (This part is left for you to implement based on your requirements)
        pass

    return render(request, 'edit_order.html', {
        'order': order,
        'order_items': order_items,
    })  
def delete_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('dashboard')

    return render(request, 'delete_product.html', {'product': product}) 

# Only allow staff

@user_passes_test(lambda u: u.is_staff)
def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = User.objects.filter(is_superuser=False)

    if search_query:
        customers = customers.filter(username__icontains=search_query)

    paginator = Paginator(customers.order_by('-date_joined'), 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

@user_passes_test(lambda u: u.is_staff)
def export_customers_csv(request):
    customers = User.objects.filter(is_superuser=False).order_by('-date_joined')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Date Joined', 'Active'])

    for customer in customers:
        writer.writerow([customer.username, customer.email, customer.date_joined, customer.is_active])

    return response

@user_passes_test(lambda u: u.is_staff)
def toggle_customer_status(request, user_id):
    customer = get_object_or_404(User, pk=user_id)
    customer.is_active = not customer.is_active
    customer.save()
    messages.success(request, f"Customer {'activated' if customer.is_active else 'blocked'} successfully.")
    return redirect('customer_list')