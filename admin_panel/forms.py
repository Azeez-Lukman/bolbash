import os
from django import forms
from booking.models import ServiceCategory, Service, BusinessHours, BlockedDate, Booking
from academy.models import CourseCategory, Course, Module, Lesson, Enrollment, Certificate
from shop.models import ProductCategory, Product, Order

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
FORBIDDEN_EXTENSIONS = ['.exe', '.php', '.py', '.sh', '.html', '.js', '.dll', '.svg', '.bat', '.cmd', '.vbs', '.phar']
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


def validate_image_file(image_file):
    """
    Validates uploaded image file extension and size limit.
    Blocks executable, script, and non-image files.
    """
    if not image_file or not hasattr(image_file, 'name'):
        return image_file

    ext = os.path.splitext(image_file.name)[1].lower()

    if ext in FORBIDDEN_EXTENSIONS or ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise forms.ValidationError(
            f"Invalid file extension '{ext}'. Only JPEG, PNG, and WebP images (.jpg, .jpeg, .png, .webp) are allowed."
        )

    if hasattr(image_file, 'size') and image_file.size > MAX_IMAGE_SIZE_BYTES:
        raise forms.ValidationError(
            f"File size ({image_file.size / (1024 * 1024):.1f}MB) exceeds maximum allowed limit of 5MB."
        )

    return image_file


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'short_description', 'description', 'price', 'duration', 'featured', 'active', 'image', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minutes'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def clean_image(self):
        return validate_image_file(self.cleaned_data.get('image'))


class BusinessHoursForm(forms.ModelForm):
    class Meta:
        model = BusinessHours
        fields = ['opening_time', 'closing_time', 'is_active']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class BlockedDateForm(forms.ModelForm):
    class Meta:
        model = BlockedDate
        fields = ['date', 'reason', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'reason': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Public Holiday, Salon Renovation'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status', 'payment_status', 'customer_note']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'customer_note': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['name', 'description', 'icon', 'order', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Emoji or icon name'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'short_description', 'full_description', 'thumbnail', 'duration', 'price', 'format_type', 'learning_outcomes', 'target_audience', 'prerequisites', 'active', 'featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-input'}),
            'full_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 4 Weeks'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'format_type': forms.Select(attrs={'class': 'form-select'}),
            'learning_outcomes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'One outcome per line'}),
            'target_audience': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'One target profile per line'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_thumbnail(self):
        return validate_image_file(self.cleaned_data.get('thumbnail'))


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['course', 'title', 'description', 'order']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'content', 'video_url', 'order', 'is_preview']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6}),
            'video_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'description', 'icon', 'order', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'short_description', 'full_description', 'price', 'image', 'stock_quantity', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={'class': 'form-input'}),
            'full_description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_image(self):
        return validate_image_file(self.cleaned_data.get('image'))

    def clean_stock_quantity(self):
        stock = self.cleaned_data.get('stock_quantity')
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return stock


class StockUpdateForm(forms.Form):
    stock_quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': 0})
    )


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status', 'payment_status']
        widgets = {
            'order_status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
        }
