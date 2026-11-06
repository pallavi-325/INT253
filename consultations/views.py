from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, DetailView
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from accounts.permissions import DoctorRequiredMixin, RoleRequiredMixin
from appointments.models import Appointment
from .models import Consultation, TreatmentPlan
from .forms import ConsultationAssessmentForm, TreatmentPlanForm
from .services.pdf_generator import render_consultation_pdf

class DoctorConsultationWorkspaceView(DoctorRequiredMixin, View):
    template_name = 'consultations/doctor_workspace.html'

    def get_appointment(self, appointment_id):
        return get_object_or_404(
            Appointment.objects.select_related('child', 'parent').prefetch_related('skin_images'),
            pk=appointment_id,
            doctor=self.request.user
        )

    def get(self, request, appointment_id):
        appointment = self.get_appointment(appointment_id)
        consultation, _ = Consultation.objects.get_or_create(
            appointment=appointment,
            defaults={'doctor': request.user}
        )
        treatment_plan, _ = TreatmentPlan.objects.get_or_create(consultation=consultation)

        consultation_form = ConsultationAssessmentForm(instance=consultation)
        treatment_form = TreatmentPlanForm(instance=treatment_plan)

        context = {
            'appointment': appointment,
            'child': appointment.child,
            'consultation': consultation,
            'treatment_plan': treatment_plan,
            'consultation_form': consultation_form,
            'treatment_form': treatment_form,
            'skin_images': appointment.skin_images.all(),
            'ai_analyses': getattr(appointment, 'ai_analyses', None).all() if hasattr(appointment, 'ai_analyses') else [],
        }
        return render(request, self.template_name, context)

    def post(self, request, appointment_id):
        appointment = self.get_appointment(appointment_id)
        consultation, _ = Consultation.objects.get_or_create(
            appointment=appointment,
            defaults={'doctor': request.user}
        )
        treatment_plan, _ = TreatmentPlan.objects.get_or_create(consultation=consultation)

        consultation_form = ConsultationAssessmentForm(request.POST, instance=consultation)
        treatment_form = TreatmentPlanForm(request.POST, instance=treatment_plan)

        if consultation_form.is_valid() and treatment_form.is_valid():
            with transaction.atomic():
                saved_consultation = consultation_form.save(commit=False)
                saved_consultation.doctor = request.user
                
                is_finalize_action = 'finalize' in request.POST
                if is_finalize_action:
                    saved_consultation.finalize()
                else:
                    saved_consultation.save()

                treatment_form.save()

            if is_finalize_action:
                messages.success(request, "Consultation successfully finalized and released to parents.")
                return redirect('appointments:doctor_dashboard')
            else:
                messages.info(request, "Clinical draft notes saved.")
                return redirect('consultations:doctor_workspace', appointment_id=appointment.id)

        context = {
            'appointment': appointment,
            'child': appointment.child,
            'consultation': consultation,
            'treatment_plan': treatment_plan,
            'consultation_form': consultation_form,
            'treatment_form': treatment_form,
            'skin_images': appointment.skin_images.all(),
        }
        return render(request, self.template_name, context)


class ParentConsultationDetailView(RoleRequiredMixin, DetailView):
    model = Consultation
    template_name = 'consultations/parent_report_detail.html'
    context_object_name = 'consultation'
    allowed_roles = ['PARENT', 'DOCTOR']

    def get_object(self, queryset=None):
        consultation = super().get_object(queryset)
        user = self.request.user
        
        # Security: Parent can only view their own child's report once finalized
        if user.is_parent():
            if consultation.appointment.parent != user:
                raise PermissionDenied("You do not have access to this report.")
            if not consultation.is_finalized:
                raise Http404("This consultation report is still pending clinician review.")
        elif user.is_doctor():
            if consultation.doctor != user and not user.is_superuser:
                raise PermissionDenied("You are not the designated physician for this consultation.")
        return consultation


class DownloadReportPDFView(RoleRequiredMixin, View):
    allowed_roles = ['PARENT', 'DOCTOR']

    def get(self, request, pk):
        consultation = get_object_or_404(Consultation, pk=pk)
        user = request.user

        # Access check
        if user.is_parent() and consultation.appointment.parent != user:
            raise PermissionDenied("Access denied.")
        if user.is_doctor() and consultation.doctor != user and not user.is_superuser:
            raise PermissionDenied("Access denied.")

        pdf_bytes = render_consultation_pdf(consultation)
        filename = f"CareNest_Report_Case_{consultation.appointment.id}.pdf"
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
