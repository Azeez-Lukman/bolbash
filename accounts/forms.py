from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import CustomerProfile


class CustomerRegistrationForm(forms.ModelForm):
    """
    Form for new salon customer account registration.
    Creates Django User and linked CustomerProfile.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'Last Name',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'name@example.com',
        })
    )
    phone_number = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': '08168956606',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'House / Street address',
            'rows': 2,
        })
    )
    city = forms.CharField(
        max_length=100,
        initial='Ibadan',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'City',
        })
    )
    state = forms.CharField(
        max_length=100,
        initial='Oyo State',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'State',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': '••••••••',
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': '••••••••',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise ValidationError("An account with this email address already exists. Please log in or use another email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please verify and try again.")
        return cleaned_data


class CustomerProfileForm(forms.ModelForm):
    """
    Form for updating customer profile details (first_name, last_name, email, phone_number, address, city, state).
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )
    phone_number = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'rows': 3,
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
        })
    )

    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'city', 'state']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.user = user

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if hasattr(self, 'user') and self.user:
            if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
                raise ValidationError("Another account is already using this email address.")
        return email


class CustomerLoginForm(AuthenticationForm):
    """
    Styled login form for customers.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': 'Your Email Address',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )
