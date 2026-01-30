from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('flats/', views.manage_flats, name='manage_flats'),
    path('services/', views.manage_services, name='manage_services'),
    path('workers/approvals/', views.worker_approvals, name='worker_approvals'),
    path('requests/', views.admin_requests, name='admin_requests'),
    path('residents/', views.view_residents, name='view_residents'),
    path('worker-ratings/', views.worker_ratings, name='worker_ratings'),
    path('worker-performance/', views.worker_performance, name='worker_performance'),
]
