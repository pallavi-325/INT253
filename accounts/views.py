from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ParentRegistrationForm, DoctorRegistrationForm, CustomLoginForm

class RoleBasedRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_doctor():
            return redirect('appointments:doctor_dashboard')
        elif user.is_parent():
            return redirect('patients:parent_dashboard')
        elif user.is_admin():
            return redirect('/admin/')
        return redirect('home')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard_redirect')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class ParentRegisterView(CreateView):
    template_name = 'accounts/register_parent.html'
    form_class = ParentRegistrationForm
    success_url = reverse_lazy('patients:parent_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome to CareNest, {user.first_name or user.username}! Your parent account is active.")
        return redirect(self.success_url)


class DoctorRegisterView(CreateView):
    template_name = 'accounts/register_doctor.html'
    form_class = DoctorRegistrationForm
    success_url = reverse_lazy('appointments:doctor_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Welcome, Dr. {user.last_name or user.username}! Your clinician account has been initialized.")
        return redirect(self.success_url)
