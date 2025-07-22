from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings

class GmailContact(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name or self.email


class IncomingEmails(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    sender = models.ForeignKey("GmailContact", on_delete=models.CASCADE, related_name='sent_emails', blank=True, null=True)
    reciver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_emails", blank=True, null=True)

    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)
    snippet = models.TextField(blank=True)

    timestamp = models.DateTimeField()  # When you fetched it or parsed Date header
    internal_date = models.DateTimeField()  # From Gmail internal timestamp

    message_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # Uniqueness here is 🔐
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    in_reply_to = models.CharField(max_length=255, blank=True, null=True)

    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    should_reply = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True)

    label_ids = models.JSONField(default=list, blank=True, null=True)
    headers = models.JSONField(default=dict, blank=True, null=True)

    reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)  
    
    is_outgoing = models.BooleanField(default=False)
    is_reply_generated_by_agent = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)  

    def __str__(self):
        return f"Email from {self.sender} - {self.subject} with uuid: {self.uuid}"


class GmailSyncState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    history_id = models.CharField(max_length=255, blank=True, null=True)
    last_synced = models.DateTimeField(auto_now=True)



    
    
    