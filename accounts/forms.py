from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import DoctorProfile, ParentProfile

User = get_user_model()

TAILWIND_INPUT_CLASS = (
    "w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors text-sm"
)

TAILWIND_CHECKBOX_CLASS = (
    "w-4 h-4 text-teal-600 bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 "
    "rounded focus:ring-teal-500"
)

class ParentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Jane'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Doe'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'jane.doe@example.com'}))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': '+1 (555) 000-0000'}))
    emergency_contact = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Emergency phone number'}))
    consent_to_telehealth = forms.BooleanField(
        required=True,
        initial=True,
        label="I consent to pediatric teledermatology services and verify I am the legal parent or guardian.",
        widget=forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX_CLASS})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': 'janedoe'})
        self.fields['password1'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': '••••••••'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PARENT
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
            profile, _ = ParentProfile.objects.get_or_create(user=user)
            profile.emergency_contact = self.cleaned_data.get('emergency_contact', '')
            profile.consent_to_telehealth = self.cleaned_data.get('consent_to_telehealth', True)
            profile.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Dr. Sarah'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Connor'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'dr.connor@hospital.org'}))
    license_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'MD-98765432'}))
    specialization = forms.CharField(max_length=120, initial="Pediatric Atopic Dermatitis & Eczema", widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS}))
    experience_years = forms.IntegerField(min_value=1, initial=5, widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASS}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': TAILWIND_INPUT_CLASS, 'rows': 3, 'placeholder': 'Clinical background...'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': 'drsarah'})
        self.fields['password1'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': TAILWIND_INPUT_CLASS, 'placeholder': '••••••••'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, _ = DoctorProfile.objects.get_or_create(user=user)
            profile.license_number = self.cleaned_data['license_number']
            profile.specialization = self.cleaned_data['specialization']
            profile.experience_years = self.cleaned_data['experience_years']
            profile.bio = self.cleaned_data.get('bio', '')
            profile.save()
        return user


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': TAILWIND_INPUT_CLASS,
            'placeholder': 'Username or Email'
        })
        self.fields['password'].widget.attrs.update({
            'class': TAILWIND_INPUT_CLASS,
            'placeholder': '••••••••'
        })

