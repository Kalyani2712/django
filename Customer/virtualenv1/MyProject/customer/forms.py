from django import forms
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

# Registration Form
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, label="User Type", initial=1)

    class Meta:
        model = User
        fields = ['username', 'email', 'user_type']  # Add 'user_type' to the form fields

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        user.user_type = int(self.cleaned_data['user_type'])  # Set user type from the form input
        
        if commit:
            user.save()
        return user

# Login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

# Product Form (For admin adding products)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock',  'image', 'color', 'offer'       ]

class BulkUploadForm(forms.Form):
    csv_file = forms.FileField()