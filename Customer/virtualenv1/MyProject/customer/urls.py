# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_customer, name='register'),
    path('login/', views.login_customer, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard_customer, name='dashboard'),
    path('add/', views.add_item, name='add_item'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),  # ✅

    path('profile/', views.profile, name='profile'),

    # ——————————————— Added routes ———————————————
    path('cart/', views.cart, name='cart'),
    path('notifications/', views.notifications, name='notifications'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('edit-order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:user_id>/toggle/', views.toggle_customer_status, name='toggle_customer_status'),
]
