from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

SERVICE_CATEGORIES = (
    ('Plumbing', 'Plumbing'),
    ('Electrical', 'Electrical'),
    ('Cleaning', 'Cleaning'),
    ('Carpentry', 'Carpentry'),
    ('Pest Control', 'Pest Control'),
    ('Babysitting & Care Services', 'Babysitting & Care Services'),
    ('Locksmith & Key Services', 'Locksmith & Key Services'),
    ('Doorstep Vehicle Wash and services', 'Doorstep Vehicle Wash and services'),
    ('Home Appliance Repair Services', 'Home Appliance Repair Services'),
    ('Grocery & Daily Essentials Delivery', 'Grocery & Daily Essentials Delivery'),
    ('Others', 'Others'),
)

class FlatLevel(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="e.g. 1A, 1B, 2C")

    def __str__(self):
        return self.name

class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g. Plumbing, Electrical, Cleaning")
    description = models.TextField(blank=True, help_text="Brief description of this service")
    is_active = models.BooleanField(default=True, help_text="Inactive services won't appear in registration")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class WorkerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, help_text="Select your primary service")
    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    
    @property
    def average_rating(self):
        ratings = Feedback.objects.filter(booking__worker=self.user)
        if not ratings.exists():
            return 0.0
        return sum([r.rating for r in ratings]) / ratings.count()

    def __str__(self):
        return f"{self.user.username} - {self.service_type.name}"

class ServiceRequest(models.Model):
    PRIORITY_CHOICES = (
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    category = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.resident.username} ({self.priority})"

class Booking(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='booking')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    rejection_reason = models.TextField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.service_request.category} by {self.worker.username}"

class DummyPayment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    is_confirmed = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {'Paid' if self.is_confirmed else 'Pending'}"

class Feedback(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Booking {self.booking.id} - Rating: {self.rating}"
