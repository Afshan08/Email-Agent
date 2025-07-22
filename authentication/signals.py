from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialLogin
from .models import GoogleAccount, AuthenticateDevice, User
from django.db import transaction
import json
from django.utils.crypto import get_random_string
from django.utils import timezone
from .models import GoogleToken
from .utils import store_tokens, get_valid_access_token, get_gmail_messages


@transaction.atomic
@receiver(pre_social_login)
def pre_social_login_handler(sender, request, sociallogin, **kwargs):
    if sociallogin.account.provider != 'google':
        return
    
    user_data = sociallogin.account.extra_data
    email = user_data.get('email')
    name = user_data.get('name')
    username = user_data.get("name") or email.split("@")[0]
    google_id = user_data.get("sub")
    access_token = sociallogin.token.token
    refresh_token = sociallogin.token.token_secret
    print(f"\n\nAccess Token  : {access_token}\n\n")
    print(f"Refresh Token : {refresh_token}\n\n")
    
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        sociallogin.connect(request, existing_user)
        store_tokens(request, sociallogin.user, access_token=access_token, refresh_token=refresh_token)
        return

    # Handle username conflicts
    if not sociallogin.user.pk:
        if User.objects.filter(username=username).exists():
            username += get_random_string(4)
        sociallogin.user.username = username
        sociallogin.user.email = email
        sociallogin.user.save()

    # Save tokens after user is saved
    

    # Get or create GoogleAccount
    google_account, created = GoogleAccount.objects.get_or_create(
        google_id=google_id,
        defaults={
            'email': email,
            'has_access': True,
            'devices': [],
            'name': name,
            'user': sociallogin.user
        }
    )
    
    if not created:
        google_account.name = name
        google_account.has_access = True
        if not google_account.user:
            google_account.user = sociallogin.user
        google_account.save()

    # Check token expiry
    user_token = GoogleToken.objects.filter(user=sociallogin.user).first()
    if user_token and user_token.is_expired():
        get_valid_access_token(request, sociallogin.user)

    # Track device
    create_device_record(request, google_account)


# Alternative: Use Django's built-in user login signal
from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Called after any user login (including social login)"""
    # Check if this was a social login by checking session
    if 'socialaccount_sociallogin' in request.session:
        # This was a social login, handle accordingly
        try:
            google_account = GoogleAccount.objects.get(email=user.email)
            # Update last login time (this happens automatically with auto_now=True)
            google_account.last_login = timezone.now()
            # Track device if not already tracked in pre_social_login
        except GoogleAccount.DoesNotExist:
            print("Pre social login did not worked as expected")
            # Fallback - shouldn't happen if pre_social_login worked
            pass
        

def create_device_record(request, google_account):
    """Create device tracking record"""
    # Get device info from request
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip = get_client_ip(request)
    
    # Simple parsing (you can make this more sophisticated)
    browser = "Unknown"
    os = "Unknown"
    device_type = "Desktop"
    
    if 'Chrome' in user_agent:
        browser = "Chrome"
    elif 'Firefox' in user_agent:
        browser = "Firefox"
    elif 'Safari' in user_agent:
        browser = "Safari"
    
    if 'Windows' in user_agent:
        os = "Windows"
    elif 'Mac' in user_agent:
        os = "macOS"
    elif 'Linux' in user_agent:
        os = "Linux"
    elif 'Android' in user_agent:
        os = "Android"
        device_type = "Mobile"
    elif 'iPhone' in user_agent:
        os = "iOS"
        device_type = "Mobile"
    
    # Create device record
    AuthenticateDevice.objects.create(
        user=google_account.user,
        browser=browser,
        os=os,
        device_type=device_type,
        ip=ip,
        
    )
    
    # Update devices list in GoogleAccount
    device_info = f"{browser} on {os}"
    if device_info not in google_account.devices:
        google_account.devices.append(device_info)
        google_account.save()

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip