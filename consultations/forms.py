from django import forms
from .models import Consultation, TreatmentPlan

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

TAILWIND_CHECKBOX = (
    "w-4 h-4 text-teal-600 bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 rounded focus:ring-teal-500"
)

class ConsultationAssessmentForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['clinical_assessment', 'differential_diagnosis', 'severity', 'clinical_notes']
        widgets = {
            'clinical_assessment': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 4,
                'placeholder': 'Primary clinical assessment, e.g. Atopic dermatitis flare-up with mild secondary xerosis on bilateral antecubital fossa...'
            }),
            'differential_diagnosis': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 2,
                'placeholder': 'e.g. Contact dermatitis, Scabies, Pityriasis alba'
            }),
            'severity': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'clinical_notes': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 2,
                'placeholder': 'Confidential clinician notes (internal only)...'
            }),
        }


class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = [
            'prescribed_medications',
            'care_instructions',
            'warning_signs',
            'follow_up_recommended',
            'follow_up_date',
            'follow_up_instructions'
        ]
        widgets = {
            'prescribed_medications': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 3,
                'placeholder': 'e.g. Hydrocortisone 1% ointment: Apply thin layer to affected red areas twice daily for 5 days. Emollient ointment: Apply liberally within 3 mins after bathing.'
            }),
            'care_instructions': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 3,
                'placeholder': 'Lukewarm daily baths (under 10 minutes). Avoid bubble baths and scented laundry detergents. Dress child in breathable cotton clothing.'
            }),
            'warning_signs': forms.Textarea(attrs={
                'class': TAILWIND_INPUT, 'rows': 2,
            }),
            'follow_up_recommended': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
            'follow_up_date': forms.DateInput(attrs={'class': TAILWIND_INPUT, 'type': 'date'}),
            'follow_up_instructions': forms.TextInput(attrs={
                'class': TAILWIND_INPUT,
                'placeholder': 'e.g. Book follow-up consultation in 2 weeks if lesions do not resolve.'
            }),
        }

