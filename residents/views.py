from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import ServiceRequest, Booking, DummyPayment, Feedback, SERVICE_CATEGORIES
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
        category = request.POST.get('category')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        
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
        
    return render(request, 'residents/create_request.html', {'categories': SERVICE_CATEGORIES})

@login_required
def resident_history(request):
    if request.user.role != 'RESIDENT':
        return redirect('dashboard_redirect')
    
    requests = ServiceRequest.objects.filter(resident=request.user).order_by('-created_at')
    return render(request, 'residents/history.html', {'requests': requests})

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
