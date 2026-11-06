from django import forms
from .models import ChildProfile, SkinImage
from appointments.models import Appointment

TAILWIND_INPUT = (
    "w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors text-sm"
)

TAILWIND_SELECT = (
    "w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 "
    "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 "
    "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors text-sm"
)

class ChildProfileForm(forms.ModelForm):
    class Meta:
        model = ChildProfile
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'known_allergies',
            'previous_skin_conditions',
            'current_medications',
            'medical_history_notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Leo'}),
            'last_name': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Doe'}),
            'date_of_birth': forms.DateInput(attrs={'class': TAILWIND_INPUT, 'type': 'date'}),
            'gender': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'blood_group': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'known_allergies': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 2, 'placeholder': 'e.g. Penicillin, Peanuts, Fragrance-based soaps'}),
            'previous_skin_conditions': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 2, 'placeholder': 'e.g. Infantile eczema on cheeks at 6 months'}),
            'current_medications': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 2, 'placeholder': 'e.g. Cetaphil cream, Hydrocortisone 0.5%'}),
            'medical_history_notes': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 3, 'placeholder': 'General health details, asthma, family allergies...'}),
        }


class SkinImageUploadForm(forms.ModelForm):
    class Meta:
        model = SkinImage
        fields = ['child', 'appointment', 'image', 'body_part', 'view_type', 'notes']
        widgets = {
            'child': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'appointment': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-teal-700 dark:file:bg-teal-950/50 dark:file:text-teal-300 hover:file:bg-teal-100',
                'accept': 'image/png,image/jpeg,image/webp'
            }),
            'body_part': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'view_type': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'notes': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 2, 'placeholder': 'e.g. Noticed redness 2 days ago, child has been scratching at night...'}),
        }

    def __init__(self, *args, parent_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_user:
            self.fields['child'].queryset = ChildProfile.objects.for_parent(parent_user)
            self.fields['appointment'].queryset = Appointment.objects.filter(parent=parent_user)
            self.fields['appointment'].required = False
