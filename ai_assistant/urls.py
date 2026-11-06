from django.urls import path
from .views import (
    SymptomChatView,
    SymptomChatAPIView,
    AnalyzeSkinImageAPIView,
    GenerateConsultationSummaryAPIView,
    ApproveConsultationSummaryAPIView,
)

app_name = 'ai_assistant'

urlpatterns = [
    path('chat/', SymptomChatView.as_view(), name='symptom_chat'),
    path('api/chat/', SymptomChatAPIView.as_view(), name='api_chat'),
    path('api/analyze-image/<int:image_id>/', AnalyzeSkinImageAPIView.as_view(), name='api_analyze_image'),
    path('api/generate-summary/<int:consultation_id>/', GenerateConsultationSummaryAPIView.as_view(), name='api_generate_summary'),
    path('api/approve-summary/<int:analysis_id>/', ApproveConsultationSummaryAPIView.as_view(), name='api_approve_summary'),
]
