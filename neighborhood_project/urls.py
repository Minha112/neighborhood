from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', lambda r: redirect('login')),
    path('accounts/', include('accounts.urls')),
    path('resident/', include('residents.urls')),
    path('worker/', include('workers.urls')),
    path('administrator/', include('administrator.urls')),
]
