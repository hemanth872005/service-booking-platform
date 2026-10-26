from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Service, AvailabilitySlot, Booking, Review

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    phone = forms.CharField(max_length=20, required=False)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "phone", "password1", "password2")
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, role=self.cleaned_data["role"], phone=self.cleaned_data["phone"])
        return user

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "category", "description", "price", "duration_minutes"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

class SlotForm(forms.ModelForm):
    start_time = forms.DateTimeField(input_formats=["%Y-%m-%dT%H:%M"], widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    end_time = forms.DateTimeField(input_formats=["%Y-%m-%dT%H:%M"], widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))
    class Meta:
        model = AvailabilitySlot
        fields = ["service", "start_time", "end_time"]
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["service"].queryset = Service.objects.filter(provider=user, active=True)
    def clean(self):
        data = super().clean()
        start, end = data.get("start_time"), data.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")
        return data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["notes"]
        widgets = {"notes": forms.TextInput(attrs={"placeholder": "Optional details (max 300 characters)"})}

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={"min": 1, "max": 5}))
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 2, "placeholder": "Share your experience"})}
