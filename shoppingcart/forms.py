from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)

class OrderPaymentForm(forms.Form):
    PAYMENT_CHOICES = (
        ('razorpay', 'Razorpay'),
        # Add other payment methods as needed
    )
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES)