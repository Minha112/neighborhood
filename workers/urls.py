from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('task/<int:booking_id>/<str:action>/', views.handle_request, name='handle_task'),
    path('availability/toggle/', views.toggle_availability, name='toggle_availability'),
    path('profile/', views.worker_profile, name='worker_profile'),
]
