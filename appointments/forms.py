from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment
from patients.models import ChildProfile

User = get_user_model()

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

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'child',
            'doctor',
            'scheduled_date',
            'scheduled_time',
            'chief_complaint',
            'duration_of_symptoms',
            'severity'
        ]
        widgets = {
            'child': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'doctor': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'scheduled_date': forms.DateInput(attrs={'class': TAILWIND_INPUT, 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': TAILWIND_INPUT, 'type': 'time'}),
            'chief_complaint': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Dry red patches on face & elbows'}),
            'duration_of_symptoms': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 4 days'}),
            'severity': forms.Select(attrs={'class': TAILWIND_SELECT}),
        }

    def __init__(self, *args, parent_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if parent_user:
            self.fields['child'].queryset = ChildProfile.objects.for_parent(parent_user)
        self.fields['doctor'].queryset = User.objects.filter(role=User.Role.DOCTOR)


class AppointmentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': TAILWIND_SELECT})
        }

