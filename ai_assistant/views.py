import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import View, TemplateView
from django.utils import timezone
from accounts.permissions import ParentRequiredMixin, DoctorRequiredMixin, RoleRequiredMixin
from patients.models import ChildProfile, SkinImage
from appointments.models import Appointment
from consultations.models import Consultation
from .models import AIAnalysis
from .services import OpenAISymptomAssistant, OpenAIVisionAssistant, OpenAIConsultationSummarizer

class SymptomChatView(ParentRequiredMixin, TemplateView):
    template_name = 'ai_assistant/symptom_chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child_id = self.request.GET.get('child')
        appointment_id = self.request.GET.get('appointment')
        
        children = ChildProfile.objects.for_parent(self.request.user)
        selected_child = children.filter(id=child_id).first() if child_id else children.first()
        
        context['children'] = children
        context['selected_child'] = selected_child
        context['appointment_id'] = appointment_id
        return context


class SymptomChatAPIView(ParentRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        child_id = data.get('child_id')
        child = get_object_or_404(ChildProfile, pk=child_id, parent=request.user)
        
        conversation_history = data.get('conversation_history', [])
        new_message = data.get('message', '').strip()
        appointment_id = data.get('appointment_id')

        if new_message:
            conversation_history.append({'role': 'user', 'content': new_message})

        child_context = {
            'name': child.full_name,
            'age': f"{child.date_of_birth} (DOB)",
            'allergies': child.known_allergies or "None"
        }

        assistant = OpenAISymptomAssistant()
        ai_result = assistant.generate_chat_response(conversation_history, child_context)

        conversation_history.append({'role': 'assistant', 'content': ai_result.get('reply', '')})

        appointment = None
        if appointment_id:
            appointment = Appointment.objects.filter(pk=appointment_id, parent=request.user).first()

        summary_data = ai_result.get('structured_summary', {})
        status = AIAnalysis.Status.FLAGGED if summary_data.get('red_flag_alert') else AIAnalysis.Status.COMPLETED

        analysis, _ = AIAnalysis.objects.get_or_create(
            child=child,
            appointment=appointment,
            analysis_type=AIAnalysis.AnalysisType.SYMPTOM_CHAT,
            defaults={
                'input_context': {'history': conversation_history},
                'structured_output': summary_data,
                'status': status
            }
        )
        analysis.input_context = {'history': conversation_history}
        analysis.structured_output = summary_data
        analysis.status = status
        analysis.save()

        return JsonResponse({
            'reply': ai_result.get('reply', ''),
            'is_complete': ai_result.get('is_complete', False),
            'structured_summary': summary_data,
            'analysis_id': analysis.id,
            'conversation_history': conversation_history
        })


class AnalyzeSkinImageAPIView(DoctorRequiredMixin, View):
    def post(self, request, image_id):
        skin_image = get_object_or_404(SkinImage, pk=image_id)
        
        vision_assistant = OpenAIVisionAssistant()
        result = vision_assistant.analyze_skin_image(skin_image)

        analysis = AIAnalysis.objects.create(
            child=skin_image.child,
            appointment=skin_image.appointment,
            analysis_type=AIAnalysis.AnalysisType.IMAGE_OBSERVATION,
            input_context={'image_id': skin_image.id, 'body_part': skin_image.body_part},
            structured_output=result,
            status=AIAnalysis.Status.COMPLETED
        )

        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'result': result
        })


class GenerateConsultationSummaryAPIView(DoctorRequiredMixin, View):
    def post(self, request, consultation_id):
        consultation = get_object_or_404(Consultation, pk=consultation_id, doctor=request.user)

        summarizer = OpenAIConsultationSummarizer()
        summary = summarizer.generate_summary(consultation)

        analysis, _ = AIAnalysis.objects.get_or_create(
            child=consultation.appointment.child,
            appointment=consultation.appointment,
            analysis_type=AIAnalysis.AnalysisType.CONSULT_SUMMARY,
            defaults={
                'structured_output': summary,
                'status': AIAnalysis.Status.PENDING,
                'doctor_reviewed': False
            }
        )
        analysis.structured_output = summary
        analysis.doctor_reviewed = False
        analysis.save()

        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'summary': summary,
            'doctor_reviewed': analysis.doctor_reviewed
        })


class ApproveConsultationSummaryAPIView(DoctorRequiredMixin, View):
    def post(self, request, analysis_id):
        analysis = get_object_or_404(
            AIAnalysis,
            pk=analysis_id,
            analysis_type=AIAnalysis.AnalysisType.CONSULT_SUMMARY
        )
        # Ensure only the assigned doctor can approve
        if analysis.appointment and analysis.appointment.doctor != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        analysis.doctor_reviewed = True
        analysis.reviewed_at = timezone.now()
        analysis.status = AIAnalysis.Status.COMPLETED
        analysis.save()

        return JsonResponse({
            'success': True,
            'message': 'AI Consultation Summary approved and verified by physician.',
            'reviewed_at': analysis.reviewed_at.isoformat()
        })
