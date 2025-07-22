from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class GoogleAccount(models.Model):
    """A model to store Google account information for users and 
    authenticate the user to site

    Args:
        id: primary_key (Django makes them automatically)
        user: google_feeded user
        has_access: boolean to check if the user is authenticated
        devices: a list of devices that the user has authenticated with
        
        Extension of Django User for Google-specific data
        
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_profile', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    has_access = models.BooleanField(default=True)  # User creation implies access
    devices = models.JSONField(default=list, blank=True)
    google_id = models.CharField(max_length=100, unique=True, null=True)  # Store Google's user ID
    email = models.EmailField(unique=True, null=True)
    
    
    def __str__(self):

        return f"{self.user}'s Google Profile"
    

class GoogleToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()

    def is_expired(self):
        return timezone.now() >= self.token_expiry   
    
    def __str__(self):
        return f"The seceret token to {self.user.username}"


    
class AuthenticateDevice(models.Model):
    """Track user devices - linked to Django User"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100) 
    device_type = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    login_time = models.DateTimeField(auto_now_add=True)  # Use auto_now_add for creation time
    
    
    def __str__(self):
        return f"{self.user.username}'s device is registered"