from django.contrib import admin
from .models import IncomingEmails, GmailSyncState, GmailContact

# Register your models here.
admin.site.register(IncomingEmails)
admin.site.register(GmailSyncState)
admin.site.register(GmailContact)


