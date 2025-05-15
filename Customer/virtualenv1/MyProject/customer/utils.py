# customer/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f'Order Confirmation - #{order.id}'
    message = f"""
    Hi {order.customer.first_name},

    Thank you for shopping with us!

    Your order #{order.id} has been placed successfully.
    Total Amount: ₹{order.total_price}
    Payment Method: {order.payment_method}
    Status: {order.status}

    We’ll notify you once it is shipped.

    Regards,
    Flipkart Clone Team
    """
    recipient_list = [order.customer.email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
