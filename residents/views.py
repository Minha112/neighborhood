from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import ServiceRequest, Booking, DummyPayment, Feedback, ServiceType, FlatLevel
from django.contrib import messages

@login_required
def resident_dashboard(request):
    if request.user.role != 'RESIDENT':
        return redirect('dashboard_redirect')
    
    requests = ServiceRequest.objects.filter(resident=request.user).order_by('-created_at')[:5]
    return render(request, 'residents/dashboard.html', {'requests': requests})

@login_required
def create_request(request):
    if request.user.role != 'RESIDENT':
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        category_id = request.POST.get('category')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        
        category = get_object_or_404(ServiceType, id=category_id)
        
        ServiceRequest.objects.create(
            resident=request.user,
            category=category,
            priority=priority,
            description=description,
            requirements=requirements,
            status='PENDING'
        )
        messages.success(request, "Service request submitted successfully.")
        return redirect('resident_dashboard')
        
    categories = ServiceType.objects.filter(is_active=True)
    return render(request, 'residents/create_request.html', {'categories': categories})

@login_required
def resident_history(request):
    if request.user.role != 'RESIDENT':
        return redirect('dashboard_redirect')
    
    requests = ServiceRequest.objects.filter(resident=request.user).order_by('-created_at')
    return render(request, 'residents/history.html', {'requests': requests})

@login_required
def resident_profile(request):
    """View and update resident profile information"""
    if request.user.role != 'RESIDENT':
        return redirect('dashboard_redirect')
    
    flat_levels = FlatLevel.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        flat_level_id = request.POST.get('flat_level')
        
        # Validate required fields
        if not first_name or not email or not phone_number or not flat_level_id:
            messages.error(request, "All fields are required.")
            return render(request, 'residents/profile.html', {'flat_levels': flat_levels})
        
        # Update user information
        user = request.user
        user.first_name = first_name
        user.email = email
        user.phone_number = phone_number
        
        # Update flat level
        try:
            flat_level = FlatLevel.objects.get(id=flat_level_id)
            user.flat_level = flat_level
        except FlatLevel.DoesNotExist:
            messages.error(request, "Invalid flat level selected.")
            return render(request, 'residents/profile.html', {'flat_levels': flat_levels})
        
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('resident_profile')
    
    return render(request, 'residents/profile.html', {'flat_levels': flat_levels})

@login_required
def dummy_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, service_request__resident=request.user)
    
    # Check if payment already exists
    payment, created = DummyPayment.objects.get_or_create(booking=booking)
    
    if request.method == 'POST':
        payment.is_confirmed = True
        payment.save()
        messages.success(request, "Payment successful! Your booking is confirmed.")
        return redirect('resident_dashboard')
        
    return render(request, 'residents/payment.html', {'booking': booking, 'payment': payment})

@login_required
def submit_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, service_request__resident=request.user)
    
    if hasattr(booking, 'feedback'):
        messages.info(request, "Duplicate feedback is not allowed.")
        return redirect('resident_history')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Feedback.objects.create(
            booking=booking,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Thank you for your feedback!")
        return redirect('resident_history')
        
    return render(request, 'residents/feedback.html', {'booking': booking})
