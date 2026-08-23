from django import forms
from .models import Review, CustomerFeedback


class ReviewForm(forms.ModelForm):
    """
    Form for authenticated customers to submit a rating and review for a completed appointment.
    """
    RATING_CHOICES = [
        (5, '★★★★★ (5/5) — Excellent'),
        (4, '★★★★☆ (4/5) — Great'),
        (3, '★★★☆☆ (3/5) — Good'),
        (2, '★★☆☆☆ (2/5) — Fair'),
        (1, '★☆☆☆☆ (1/5) — Poor'),
    ]

    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        initial=5,
        widget=forms.Select(attrs={
            'class': 'form-select w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-sm font-semibold',
        }),
        help_text="Select your rating score from 1 to 5 stars."
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input w-full rounded-lg border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-sm',
            'placeholder': 'Share your experience at Bolbash Beauty Spot (e.g. service quality, salon environment, staff hospitality)...',
            'rows': 5,
        }),
        help_text="Provide detailed feedback about your appointment."
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if not comment:
            raise forms.ValidationError("Please provide details for your review feedback.")
        if len(comment) > 2000:
            raise forms.ValidationError("Review comment cannot exceed 2000 characters.")
        return comment


class CustomerFeedbackForm(forms.ModelForm):
    """
    Form for customers and website visitors to submit feedback, suggestions, or complaints.
    """
    category = forms.ChoiceField(
        choices=CustomerFeedback.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs font-semibold',
        })
    )
    rating = forms.TypedChoiceField(
        choices=[('', 'Optional Rating')] + ReviewForm.RATING_CHOICES,
        coerce=int,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
        })
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
            'placeholder': 'Your Full Name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
            'placeholder': 'your.email@example.com',
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
            'placeholder': 'Phone Number (Optional)',
        })
    )
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
            'placeholder': 'Feedback Subject / Topic',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input w-full rounded-xl border-brand-neutral-300 focus:border-brand-pink focus:ring-brand-pink text-xs',
            'placeholder': 'Tell us about your experience, suggestion, or feedback in detail...',
            'rows': 5,
        })
    )

    class Meta:
        model = CustomerFeedback
        fields = ['category', 'rating', 'name', 'email', 'phone', 'subject', 'message']

