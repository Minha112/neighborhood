from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from accounts.models import CustomUser
from core.models import FlatLevel, WorkerProfile, ServiceRequest, Booking, Feedback, ServiceType
from django.utils import timezone
from django.contrib import messages
from django.db.models import Avg, Count, Q

def is_admin(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = CustomUser.objects.filter(role='RESIDENT').count()
    pending_workers = WorkerProfile.objects.filter(is_approved=False).count()
    active_requests = ServiceRequest.objects.filter(status__in=['PENDING', 'ACCEPTED']).count()
    completed_requests = ServiceRequest.objects.filter(status='COMPLETED').count()
    
    recent_requests = ServiceRequest.objects.order_by('-created_at')[:8]
    
    return render(request, 'administrator/dashboard.html', {
        'total_users': total_users,
        'pending_workers': pending_workers,
        'active_requests': active_requests,
        'completed_requests': completed_requests,
        'recent_requests': recent_requests
    })

@user_passes_test(is_admin)
def manage_flats(request):
    flats = FlatLevel.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            FlatLevel.objects.create(name=name)
            messages.success(request, f"Flat {name} created.")
        return redirect('manage_flats')
    return render(request, 'administrator/flats.html', {'flats': flats})

@user_passes_test(is_admin)
def worker_approvals(request):
    pending = WorkerProfile.objects.filter(is_approved=False)
    if 'approve' in request.GET:
        prof = get_object_or_404(WorkerProfile, id=request.GET.get('approve'))
        prof.is_approved = True
        prof.save()
        messages.success(request, f"Worker {prof.user.username} approved.")
        return redirect('worker_approvals')
    
    if 'reject' in request.GET:
        prof = get_object_or_404(WorkerProfile, id=request.GET.get('reject'))
        user = prof.user
        prof.delete()
        user.delete()
        messages.warning(request, "Worker registration rejected and account removed.")
        return redirect('worker_approvals')
        
    return render(request, 'administrator/worker_approvals.html', {'pending': pending})

@user_passes_test(is_admin)
def admin_requests(request):
    all_requests = ServiceRequest.objects.all().order_by('-priority', '-created_at')
    workers = WorkerProfile.objects.filter(is_approved=True, is_available=True)
    
    # Priority allocation logic shortcut:
    # We will pass a suggested worker list for each request based on rating
    for req in all_requests:
        if req.status == 'PENDING' or req.status == 'REJECTED':
            # Find best match for this category based on rating
            suitable_workers = workers.filter(service_type=req.category)
            # Annotate with rating and order
            # (Note: real-world would use a custom manager or annotate query, 
            # here we use the property-based sorting for demo logic)
            req.suggested_workers = sorted(suitable_workers, key=lambda w: w.average_rating, reverse=True)

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        worker_user_id = request.POST.get('worker_id')
        
        service_req = get_object_or_404(ServiceRequest, id=request_id)
        worker_user = get_object_or_404(CustomUser, id=worker_user_id)
        
        # If there's an existing booking, reassign it instead of deleting
        if hasattr(service_req, 'booking'):
            b = service_req.booking
            b.worker = worker_user
            b.rejection_reason = ''
            b.assigned_at = timezone.now()
            b.save()
        else:
            # Create booking (Assignment)
            Booking.objects.create(
                service_request=service_req,
                worker=worker_user
            )
        # Update request status to ASSIGNED (waiting for worker to accept)
        service_req.status = 'ASSIGNED'
        service_req.save()

        messages.success(request, f"Task assigned to {worker_user.username}")
        return redirect('admin_requests')

    return render(request, 'administrator/requests.html', {
        'all_requests': all_requests,
        'workers': workers
    })

@user_passes_test(is_admin)
def view_residents(request):
    """View and search residents by flat level"""
    residents = CustomUser.objects.filter(role='RESIDENT').select_related('flat_level').order_by('flat_level__name', 'username')
    flat_levels = FlatLevel.objects.all().order_by('name')
    
    # Search/filter by flat level
    selected_flat = request.GET.get('flat_level')
    if selected_flat:
        residents = residents.filter(flat_level__id=selected_flat)
    
    # Search by username or phone
    search_query = request.GET.get('search')
    if search_query:
        residents = residents.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'residents': residents,
        'flat_levels': flat_levels,
        'selected_flat': selected_flat,
        'search_query': search_query,
    }
    return render(request, 'administrator/residents.html', context)

@user_passes_test(is_admin)
def worker_ratings(request):
    """View user ratings and feedback for workers"""
    # Get all feedbacks with related information
    feedbacks = Feedback.objects.select_related(
        'booking__worker',
        'booking__service_request__resident'
    ).order_by('-created_at')
    
    # Filter by worker if specified
    worker_id = request.GET.get('worker_id')
    if worker_id:
        feedbacks = feedbacks.filter(booking__worker__id=worker_id)
    
    # Get all approved workers for filter dropdown
    workers = CustomUser.objects.filter(
        role='WORKER',
        worker_profile__is_approved=True
    ).order_by('username')
    
    # Get workers with their average ratings
    worker_ratings_list = []
    for worker in workers:
        avg_rating = Feedback.objects.filter(booking__worker=worker).aggregate(Avg('rating'))['rating__avg']
        feedback_count = Feedback.objects.filter(booking__worker=worker).count()
        if avg_rating is not None or feedback_count > 0:
            worker_ratings_list.append({
                'worker': worker,
                'average_rating': avg_rating or 0,
                'feedback_count': feedback_count,
            })
    
    context = {
        'feedbacks': feedbacks,
        'workers': workers,
        'worker_ratings_list': worker_ratings_list,
        'selected_worker_id': worker_id,
    }
    return render(request, 'administrator/worker_ratings.html', context)

@user_passes_test(is_admin)
def worker_performance(request):
    """Monitor worker performance based on ratings"""
    # Get all approved workers
    workers = CustomUser.objects.filter(
        role='WORKER',
        worker_profile__is_approved=True
    ).select_related('worker_profile').order_by('username')
    
    worker_stats = []
    for worker in workers:
        profile = worker.worker_profile
        
        # Get ratings for this worker
        feedbacks = Feedback.objects.filter(booking__worker=worker)
        avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg']
        feedback_count = feedbacks.count()
        
        # Get completed jobs
        completed_jobs = Booking.objects.filter(
            worker=worker,
            service_request__status='COMPLETED'
        ).count()
        
        # Get total rejected jobs
        rejected_jobs = ServiceRequest.objects.filter(
            booking__worker=worker,
            status='REJECTED'
        ).count()
        
        worker_stats.append({
            'worker': worker,
            'profile': profile,
            'average_rating': avg_rating or 0,
            'feedback_count': feedback_count,
            'completed_jobs': completed_jobs,
            'rejected_jobs': rejected_jobs,
        })
    
    # Sort by average rating (highest first)
    worker_stats = sorted(worker_stats, key=lambda x: x['average_rating'], reverse=True)
    
    # Filter by service type if specified
    service_type = request.GET.get('service_type')
    if service_type:
        worker_stats = [w for w in worker_stats if w['profile'].service_type.name == service_type]
    
    # Get all service types from database
    service_types = ServiceType.objects.filter(is_active=True).values_list('name', flat=True)
    
    context = {
        'worker_stats': worker_stats,
        'service_types': service_types,
        'selected_service_type': service_type,
    }
    return render(request, 'administrator/worker_performance.html', context)

@user_passes_test(is_admin)
def manage_services(request):
    services = ServiceType.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                ServiceType.objects.create(name=name, description=description)
                messages.success(request, f"Service '{name}' created successfully.")
        
        elif action == 'toggle':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(ServiceType, id=service_id)
            service.is_active = not service.is_active
            service.save()
            status = "activated" if service.is_active else "deactivated"
            messages.success(request, f"Service '{service.name}' {status}.")
        
        return redirect('manage_services')
    
    return render(request, 'administrator/services.html', {'services': services})

