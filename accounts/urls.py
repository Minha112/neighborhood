from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/resident/', views.ResidentRegistrationView.as_view(), name='register_resident'),
    path('register/worker/', views.WorkerRegistrationView.as_view(), name='register_worker'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]
