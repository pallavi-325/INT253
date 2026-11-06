from django.contrib import admin
from .models import Consultation, TreatmentPlan

class TreatmentPlanInline(admin.StackedInline):
    model = TreatmentPlan
    can_delete = False

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'doctor', 'severity', 'is_finalized', 'finalized_at')
    list_filter = ('is_finalized', 'severity', 'finalized_at')
    search_fields = ('appointment__child__first_name', 'appointment__child__last_name', 'doctor__username', 'clinical_assessment')
    inlines = [TreatmentPlanInline]

@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'follow_up_recommended', 'follow_up_date')
    list_filter = ('follow_up_recommended',)
