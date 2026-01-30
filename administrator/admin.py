from django.contrib import admin
from accounts.models import CustomUser
from core.models import FlatLevel, WorkerProfile, ServiceRequest, Booking, DummyPayment, Feedback

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'flat_level', 'phone_number', 'is_staff', 'date_joined')
    list_filter = ('role', 'flat_level', 'date_joined', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        ('User Info', {'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number')}),
        ('Role & Flat', {'fields': ('role', 'flat_level')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined', 'last_login'), 'classes': ('collapse',)}),
    )
    actions = ['make_active', 'make_inactive', 'delete_selected']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    make_inactive.short_description = "Deactivate selected users"

@admin.register(FlatLevel)
class FlatLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'resident_count')
    search_fields = ('name',)
    actions = ['delete_selected']
    
    def resident_count(self, obj):
        return CustomUser.objects.filter(flat_level=obj).count()
    resident_count.short_description = 'Number of Residents'

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'is_approved', 'is_available', 'average_rating', 'total_jobs')
    list_filter = ('service_type', 'is_approved', 'is_available')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('average_rating',)
    actions = ['approve_workers', 'disapprove_workers', 'make_available', 'make_unavailable', 'delete_selected']
    
    def approve_workers(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} worker(s) approved.')
    approve_workers.short_description = "Approve selected workers"
    
    def disapprove_workers(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} worker(s) disapproved.')
    disapprove_workers.short_description = "Disapprove selected workers"
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} worker(s) marked as available.')
    make_available.short_description = "Mark selected workers as available"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} worker(s) marked as unavailable.')
    make_unavailable.short_description = "Mark selected workers as unavailable"
    
    def total_jobs(self, obj):
        return Booking.objects.filter(worker=obj.user).count()
    total_jobs.short_description = 'Total Jobs'
# ServiceRequest removed from admin list per request; keep model available to application code
# If you later want to re-enable administration for ServiceRequest, register it here again.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_request', 'worker', 'assigned_at', 'service_status')
    list_filter = ('assigned_at', 'service_request__status')
    search_fields = ('worker__username', 'service_request__resident__username')
    readonly_fields = ('assigned_at',)
    actions = ['delete_selected']
    
    def service_status(self, obj):
        return obj.service_request.status
    service_status.short_description = 'Service Status'

@admin.register(DummyPayment)
class DummyPaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'is_confirmed', 'paid_at')
    list_filter = ('is_confirmed', 'paid_at')
    search_fields = ('booking__worker__username', 'booking__service_request__resident__username')
    readonly_fields = ('paid_at',)
    actions = ['confirm_payments', 'delete_selected']
    
    def confirm_payments(self, request, queryset):
        updated = queryset.update(is_confirmed=True)
        self.message_user(request, f'{updated} payment(s) confirmed.')
    confirm_payments.short_description = "Confirm selected payments"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'resident', 'worker', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('booking__worker__username', 'booking__service_request__resident__username', 'comment')
    readonly_fields = ('booking', 'created_at')
    fieldsets = (
        ('Feedback Details', {'fields': ('booking', 'rating', 'comment')}),
        ('Timestamp', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    actions = ['delete_selected']
    
    def resident(self, obj):
        return obj.booking.service_request.resident
    resident.short_description = 'Resident'
    
    def worker(self, obj):
        return obj.booking.worker
    worker.short_description = 'Worker'
