from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('request/new/', views.create_request, name='create_request'),
    path('history/', views.resident_history, name='resident_history'),
    path('payment/<int:booking_id>/', views.dummy_payment, name='dummy_payment'),
    path('feedback/<int:booking_id>/', views.submit_feedback, name='submit_feedback'),
]
