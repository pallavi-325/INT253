from django.urls import path
from .views import (
    DoctorConsultationWorkspaceView,
    ParentConsultationDetailView,
    DownloadReportPDFView,
)

app_name = 'consultations'

urlpatterns = [
    path('workspace/<int:appointment_id>/', DoctorConsultationWorkspaceView.as_view(), name='doctor_workspace'),
    path('report/<int:pk>/', ParentConsultationDetailView.as_view(), name='parent_report'),
    path('report/<int:pk>/pdf/', DownloadReportPDFView.as_view(), name='download_pdf'),
]

