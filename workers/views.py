from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Booking, WorkerProfile, ServiceRequest, Feedback
from django.contrib import messages

@login_required
def worker_dashboard(request):
    if request.user.role != 'WORKER':
        return redirect('dashboard_redirect')
    
    profile = request.user.worker_profile
    assigned_jobs = Booking.objects.filter(worker=request.user, service_request__status__in=['ASSIGNED', 'ACCEPTED']).order_by('-assigned_at')
    # For feedback list
    recent_completed = Booking.objects.filter(worker=request.user, service_request__status='COMPLETED').order_by('-assigned_at')[:5]
    # For full history section
    all_jobs = Booking.objects.filter(worker=request.user).order_by('-assigned_at')
    
    return render(request, 'workers/dashboard.html', {
        'profile': profile,
        'assigned_jobs': assigned_jobs,
        'recent_completed': recent_completed,
        'all_jobs': all_jobs
    })

@login_required
def handle_request(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id, worker=request.user)
    
    if action == 'accept':
        booking.service_request.status = 'ACCEPTED'
        booking.service_request.save()
        messages.success(request, "Task accepted! Resident will now be prompted for payment.")
    
    elif action == 'reject':
        reason = request.POST.get('reason')
        if not reason:
            messages.error(request, "A reason is required to reject a task.")
            return redirect('worker_dashboard')
            
        booking.rejection_reason = reason
        booking.service_request.status = 'REJECTED'
        booking.service_request.save()
        messages.info(request, "Task rejected.")
        
    elif action == 'complete':
        # Simple security: check if paid or if bypass for simplicity
        # For this requirement, we just mark as complete
        booking.service_request.status = 'COMPLETED'
        booking.service_request.save()
        messages.success(request, "Task marked as completed!")
        
    return redirect('worker_dashboard')

@login_required
def toggle_availability(request):
    if request.user.role != 'WORKER':
        return redirect('dashboard_redirect')
        
    profile = request.user.worker_profile
    profile.is_available = not profile.is_available
    profile.save()
    
    status = "Available" if profile.is_available else "Unavailable"
    messages.info(request, f"Your status is now: {status}")
    return redirect('worker_dashboard')

@login_required
def worker_profile(request):
    """View worker profile - view only"""
    if request.user.role != 'WORKER':
        return redirect('dashboard_redirect')
        
    profile = request.user.worker_profile
    feedbacks = Feedback.objects.filter(booking__worker=request.user)
        
    return render(request, 'workers/profile.html', {
        'profile': profile,
        'feedbacks': feedbacks
    })


