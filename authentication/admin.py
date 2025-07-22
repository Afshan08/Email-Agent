from django.contrib import admin
from .models import GoogleAccount, AuthenticateDevice, GoogleToken


admin.site.site_header = "Afshan's Email Agent Admin"
admin.site.site_title = "Email Agent Portal"
admin.site.index_title = "Welcome to the Email Agent Dashboard"
# Register your models here.
admin.site.register(GoogleAccount)
admin.site.register(AuthenticateDevice)
admin.site.register(GoogleToken)