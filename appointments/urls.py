from django.urls import path
from .views import (
    DoctorDirectoryView,
    DoctorDetailView,
    AppointmentCreateView,
    ParentAppointmentListView,
    DoctorDashboardView,
    DoctorAppointmentListView,
    AppointmentDetailView,
    AppointmentStatusUpdateView,
    AppointmentCancelView,
)

app_name = 'appointments'

urlpatterns = [
    path('doctors/', DoctorDirectoryView.as_view(), name='doctor_directory'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('book/', AppointmentCreateView.as_view(), name='book_appointment'),
    path('my-appointments/', ParentAppointmentListView.as_view(), name='parent_appointment_list'),
    path('doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('doctor/schedule/', DoctorAppointmentListView.as_view(), name='doctor_appointment_list'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/status/', AppointmentStatusUpdateView.as_view(), name='appointment_status_update'),
    path('<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment_cancel'),
]
