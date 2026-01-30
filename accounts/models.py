from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('RESIDENT', 'Residential User'),
        ('WORKER', 'Service Provider (Worker)'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='RESIDENT')
    flat_level = models.ForeignKey('core.FlatLevel', on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
