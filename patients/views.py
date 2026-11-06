from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from accounts.permissions import ParentRequiredMixin, RoleRequiredMixin
from .models import ChildProfile, SkinImage
from .forms import ChildProfileForm, SkinImageUploadForm
from appointments.models import Appointment

class ParentDashboardView(ParentRequiredMixin, TemplateView):
    template_name = 'patients/parent_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        children = ChildProfile.objects.for_parent(user)
        context['children'] = children
        context['children_count'] = children.count()
        context['upcoming_appointments'] = getattr(user, 'parent_appointments', None).filter(
            status__in=['PENDING', 'CONFIRMED']
        ).order_by('scheduled_date', 'scheduled_time')[:5] if hasattr(user, 'parent_appointments') else []
        return context


class ChildListView(ParentRequiredMixin, ListView):
    model = ChildProfile
    template_name = 'patients/child_list.html'
    context_object_name = 'children'

    def get_queryset(self):
        return ChildProfile.objects.for_parent(self.request.user)


class ChildDetailView(RoleRequiredMixin, DetailView):
    model = ChildProfile
    template_name = 'patients/child_detail.html'
    context_object_name = 'child'
    allowed_roles = ['PARENT', 'DOCTOR']

    def get_queryset(self):
        user = self.request.user
        if user.is_parent():
            return ChildProfile.objects.for_parent(user)
        elif user.is_doctor() or user.is_superuser:
            return ChildProfile.objects.all()
        return ChildProfile.objects.none()


class ChildCreateView(ParentRequiredMixin, CreateView):
    model = ChildProfile
    form_class = ChildProfileForm
    template_name = 'patients/child_form.html'
    success_url = reverse_lazy('patients:child_list')

    def form_valid(self, form):
        form.instance.parent = self.request.user
        messages.success(self.request, f"Child profile for {form.instance.first_name} created successfully.")
        return super().form_valid(form)


class ChildUpdateView(ParentRequiredMixin, UpdateView):
    model = ChildProfile
    form_class = ChildProfileForm
    template_name = 'patients/child_form.html'
    success_url = reverse_lazy('patients:child_list')

    def get_queryset(self):
        return ChildProfile.objects.for_parent(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"Updated profile for {form.instance.first_name}.")
        return super().form_valid(form)


class SkinImageUploadView(ParentRequiredMixin, CreateView):
    model = SkinImage
    form_class = SkinImageUploadForm
    template_name = 'patients/upload_skin_image.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['parent_user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        child_id = self.request.GET.get('child')
        appointment_id = self.request.GET.get('appointment')
        if child_id:
            initial['child'] = child_id
        if appointment_id:
            initial['appointment'] = appointment_id
        return initial

    def form_valid(self, form):
        if form.instance.child.parent != self.request.user:
            raise PermissionDenied("You can only upload images for your registered children.")
        
        response = super().form_valid(form)
        messages.success(self.request, "Skin image uploaded successfully.")
        return response

    def get_success_url(self):
        if self.object.appointment:
            return reverse('appointments:appointment_detail', kwargs={'pk': self.object.appointment.pk})
        return reverse('patients:child_detail', kwargs={'pk': self.object.child.pk})


class SkinImageDeleteView(ParentRequiredMixin, DeleteView):
    model = SkinImage

    def get_queryset(self):
        return SkinImage.objects.filter(child__parent=self.request.user)

    def get_success_url(self):
        messages.warning(self.request, "Image deleted.")
        if self.object.appointment:
            return reverse('appointments:appointment_detail', kwargs={'pk': self.object.appointment.pk})
        return reverse('patients:child_detail', kwargs={'pk': self.object.child.pk})
