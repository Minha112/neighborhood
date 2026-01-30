from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from core.models import FlatLevel, WorkerProfile, SERVICE_CATEGORIES

class ResidentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    flat_level = forms.ModelChoiceField(queryset=FlatLevel.objects.all(), required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'phone_number', 'flat_level')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'RESIDENT'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.flat_level = self.cleaned_data['flat_level']
        if commit:
            user.save()
        return user

class WorkerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    service_type = forms.ChoiceField(choices=SERVICE_CATEGORIES, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'WORKER'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
            WorkerProfile.objects.create(
                user=user,
                service_type=self.cleaned_data['service_type'],
                bio=self.cleaned_data['bio'],
                is_approved=False # Admin must approve
            )
        return user
