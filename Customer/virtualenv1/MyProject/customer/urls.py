# urls.py
from django.urls import path
from . import views
from .views import process_return_refund
from .views import product_list
from django.conf import settings
from django.conf.urls.static import static

admin_urlpatterns = [
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
    
    path('Admincart/', views.Acart, name='Admincart'),
    path('notifications/', views.notifications, name='notifications'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('edit-order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:user_id>/toggle/', views.toggle_customer_status, name='toggle_customer_status'),
    path('bulk-upload/', views.bulk_upload_products, name='bulk_upload_products'),
    path('delete-image/<int:product_id>/', views.delete_product_image, name='delete_product_image'),
     path('manage_categories/', views.manage_categories, name='manage_categories'),
     path('export-products-csv/', views.export_products_csv, name='export_products_csv'),
    path('orders/', views.admin_orders, name='admin_orders'),
     path('products/', views.admin_products, name='admin_products'),
     path('orders/<int:order_id>/return/', process_return_refund, name='process_return_refund'),
    path('order/<int:order_id>/invoice/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
   path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
   path('image-manager/', views.image_manager, name='image_manager'),

    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('analytics/', views.analytics_dashboard, name='analytics-dashboard'),
     path('chart-data/', views.chart_data, name='chart-data'),
     
   
]

customer_urlpatterns = [
   path('customer/product_list/', views.product_list, name='product_list'),
     
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
  
]

urlpatterns = customer_urlpatterns + admin_urlpatterns