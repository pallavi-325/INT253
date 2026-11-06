from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.permissions import ParentRequiredMixin, DoctorRequiredMixin, RoleRequiredMixin
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentStatusUpdateForm
from accounts.models import DoctorProfile

User = get_user_model()

class DoctorDirectoryView(ListView):
    model = User
    template_name = 'appointments/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR).select_related('doctor_profile')


class DoctorDetailView(DetailView):
    model = User
    template_name = 'appointments/doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR)


class AppointmentCreateView(ParentRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentBookingForm
    template_name = 'appointments/book_appointment.html'
    success_url = reverse_lazy('appointments:parent_appointment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['parent_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.parent = self.request.user
            response = super().form_valid(form)
            messages.success(
                self.request,
                f"Appointment booked with Dr. {form.instance.doctor.get_full_name() or form.instance.doctor.username} on {form.instance.scheduled_date}."
            )
            return response


class ParentAppointmentListView(ParentRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/parent_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(parent=self.request.user).select_related('child', 'doctor')


class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'appointments/doctor_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.request.user
        appointments = Appointment.objects.filter(doctor=doctor).select_related('child', 'parent')
        
        today = timezone.now().date()
        context['today_appointments'] = appointments.filter(scheduled_date=today)
        context['pending_reviews'] = appointments.filter(status='PENDING')
        context['active_reviews'] = appointments.filter(status='IN_REVIEW')
        context['completed_count'] = appointments.filter(status='COMPLETED').count()
        context['recent_queue'] = appointments.order_by('-scheduled_date', '-scheduled_time')[:10]
        return context


class DoctorAppointmentListView(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/doctor_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user).select_related('child', 'parent')


class AppointmentDetailView(RoleRequiredMixin, DetailView):
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    allowed_roles = ['PARENT', 'DOCTOR']

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor():
            return Appointment.objects.filter(doctor=user)
        elif user.is_parent():
            return Appointment.objects.filter(parent=user)
        return Appointment.objects.all()


class AppointmentStatusUpdateView(DoctorRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentStatusUpdateForm
    template_name = 'appointments/appointment_status_form.html'

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user)

    def get_success_url(self):
        messages.success(self.request, f"Appointment status updated to {self.object.get_status_display()}.")
        return reverse_lazy('appointments:appointment_detail', kwargs={'pk': self.object.pk})


class AppointmentCancelView(RoleRequiredMixin, View):
    allowed_roles = ['PARENT', 'DOCTOR']

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        if request.user != appointment.parent and request.user != appointment.doctor and not request.user.is_superuser:
            messages.error(request, "Permission denied.")
            return redirect('home')
        
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = request.POST.get('cancellation_reason', 'Cancelled by user.')
        appointment.save()
        messages.warning(request, "Appointment has been cancelled.")
        
        if request.user.is_doctor():
            return redirect('appointments:doctor_appointment_list')
        return redirect('appointments:parent_appointment_list')
