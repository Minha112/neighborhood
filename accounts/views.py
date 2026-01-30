from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .forms import ResidentRegistrationForm, WorkerRegistrationForm
from django.contrib import messages

class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.role == 'WORKER':
            if not hasattr(user, 'worker_profile') or not user.worker_profile.is_approved:
                messages.error(self.request, "Your account is pending admin approval.")
                return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'ADMIN' or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.role == 'RESIDENT':
        return redirect('resident_dashboard')
    elif request.user.role == 'WORKER':
        return redirect('worker_dashboard')
    return redirect('login')

class ResidentRegistrationView(CreateView):
    form_class = ResidentRegistrationForm
    template_name = 'accounts/register_resident.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Account created successfully. Please login.")
        return super().form_valid(form)

class WorkerRegistrationView(CreateView):
    form_class = WorkerRegistrationForm
    template_name = 'accounts/register_worker.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration submitted. Awaiting admin approval.")
        return super().form_valid(form)

def logout_view(request):
    logout(request)
    return redirect('login')
