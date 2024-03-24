import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Product, Cart, Order, Payment, Customer
from .forms import CartAddProductForm, OrderPaymentForm
from django.core.exceptions import ObjectDoesNotExist

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shoppingcart/product_list.html', {'products': products})

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_product_form = CartAddProductForm(request.POST)
    if cart_product_form.is_valid():
        cart_product_form.save()
        # Add product to cart
        return redirect('shoppingcart:cart')
    return render(request, 'shoppingcart/product_list.html', {'product': product, 'cart_product_form': cart_product_form})

@login_required
def cart(request):
    try:
        customer = Customer.objects.get(user=request.user)
        cart_items = Cart.objects.filter(customer=customer)
    except ObjectDoesNotExist:
        # Handle case where customer object does not exist
        # You can create the customer object here or handle it based on your logic
        cart_items = None
    return render(request, 'shoppingcart/cart.html', {'cart_items': cart_items})


def checkout(request):
    if request.method == 'POST':
        order_payment_form = OrderPaymentForm(request.POST)
        if order_payment_form.is_valid():
            order = Order.objects.create(customer=request.user.customer, total_amount=0)  # Create a new order
            total_amount = order.total_amount
            order.total_amount = total_amount  # Set the total amount
            order.save()

            # Create a Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

            # Create a Razorpay order
            razorpay_order = client.order.create({
                'amount': int(total_amount * 100),  # Amount in paisa
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture payment
            })

            # Create a payment record for the order
            Payment.objects.create(order=order, amount=total_amount, payment_method='Razorpay')

            return render(request, 'shoppingcart/checkout.html', {
                'order_payment_form': order_payment_form,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_API_KEY
            })
    else:
        order_payment_form = OrderPaymentForm()
    return render(request, 'shoppingcart/checkout.html', {'order_payment_form': order_payment_form})

def order_success(request):
    return render(request, 'shoppingcart/order_success.html')
