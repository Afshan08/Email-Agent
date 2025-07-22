from .models import GoogleToken
from datetime import timedelta
from django.utils import timezone
import requests
from allauth.socialaccount.models import SocialToken
import base64
from agentsworkflow.models import GmailSyncState
from datetime import datetime
from email.mime.text import MIMEText
from .models import GoogleToken

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError("CLIENT_ID and CLIENT_SECRET must be set in the environment variables.")

def store_tokens(request, user, access_token, refresh_token):
    
   GoogleToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_expiry': timezone.now() + timedelta(seconds=3600),
        }
    )
        


def get_valid_access_token(user):
    token_obj = GoogleToken.objects.filter(user=user).first()
    if not token_obj:
        raise Exception("No token found for user")
    if token_obj.is_expired():
        print("Access token expired, refreshing...")
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": token_obj.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        data = response.json()

        if "access_token" in data:
            token_obj.access_token = data["access_token"]
            token_obj.token_expiry = timezone.now() + timedelta(seconds=data["expires_in"])
            token_obj.save()
        else:
            raise Exception("Token refresh failed")

    return token_obj.access_token


def get_gmail_messages(user):
    access_token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers
    )
    return response.json()

def get_gmail_history(user, sync_state: GmailSyncState):
    access_token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }


    params = {
        "startHistoryId": sync_state.history_id,
        "historyTypes": "messageAdded"
    }

    response = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/history",
        headers=headers,
        params=params
    )
    
    if response.status_code != 200:
        print("History fetch failed:", response.text)
        return None

    data = response.json()

    # Optional: Update sync state with latest historyId if available
    if "historyId" in data:
        sync_state.history_id = data["historyId"]
        sync_state.save()

    return data


def gmail_message(message_id, user):
    access_token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    msg_id = message_id
    msg_response = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
        headers=headers,
        
        )
    if msg_response.status_code != 200:
        print(f"Failed to fetch message {msg_id}: {msg_response.status_code}")
        return None

    full_msg_data = msg_response.json()
    # history = full_msg_data["messages"]["historyId"]
    # state_to_update = GmailSyncState.objects.filter(user=user).first()
    # state_to_update.history_id = history

    return full_msg_data


def clean_email_body(body):
    # Decode Base64url first if you haven't already!
    lines = body.splitlines()
    
    useful_lines = []
    for line in lines:
        if "Unsubscribe:" in line or "This email was intended for" in line:
            break  # Stop at footer or junk
        useful_lines.append(line.strip())
    
    return "\n".join([line for line in useful_lines if line])


def extract_email_details(message):
    headers = message.get("payload", {}).get("headers", [])
    subject = sender = to = ""

    for header in headers:
        name = header.get("name")
        value = header.get("value", "")
        if name.lower() == "subject":
            subject = value
        elif name.lower() == "from":
            sender = value
        elif name.lower() == "to":
            to = value

    # Decode plain text body
    parts = message.get("payload", {}).get("parts", [])
    body = ""
    clean_body = ""

    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                try:
                    decoded_bytes = base64.urlsafe_b64decode(data.encode("utf-8"))
                    body = decoded_bytes.decode("utf-8")
                    clean_body = clean_email_body(body)
                except Exception as e:
                    print(f"Body decoding failed: {e}")
            break

    # Parse timestamp
    internal_ts = message.get("internalDate")
    internal_date = datetime.fromtimestamp(int(internal_ts) / 1000) if internal_ts else None

    return {
        "message_id": message.get("id"),
        "thread_id": message.get("threadId"),
        "subject": subject,
        "sender": sender,
        "to": to,
        "body": clean_body,
        "snippet": message.get("snippet", ""),
        "internal_date": internal_date,
        "label_ids": message.get("labelIds", []),
        "headers": headers,
        "history_id": message.get("historyId")  # Might be None if not present
    }
    
    
def send_gmail_email(user, to, subject, body_text):
    """
    Send a plain text email using Gmail API on behalf of the user.
    """
    access_token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


    mime_msg = MIMEText(body_text)
    mime_msg['to'] = to
    mime_msg['from'] = user.email
    mime_msg['subject'] = subject

    # 2. Encode message
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()

    # 3. Prepare payload
    payload = {
        "raw": raw
    }

    # 4. Send the request
    response = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        print("Email sent successfully!")
        return response.json()
    else:
        print("Failed to send email:", response.status_code, response.text)
        return None
    


def reply_to_gmail_email(user, to, subject, body_text, thread_id, original_message_id):
    """
    Sends a reply email using Gmail API. Keeps it in the same thread and sets correct headers.
    """
    access_token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Ensure subject starts with "Re: "
    if not subject.lower().startswith("re:"):
        subject = "Re: " + subject

    # Construct MIME message
    mime_msg = MIMEText(body_text)
    mime_msg['to'] = to
    mime_msg['from'] = user.email
    mime_msg['subject'] = subject
    mime_msg['In-Reply-To'] = original_message_id
    mime_msg['References'] = original_message_id

    # Encode message
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()

    # Prepare payload with threadId
    payload = {
        "raw": raw,
        "threadId": thread_id
    }

    # Send request
    response = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        print("Reply sent successfully.")
        return response.json()
    else:
        print("Failed to send reply:", response.status_code, response.text)
        return None
    

def extract_email_details_from_model(request, email):
    return {
        "message_id": email.message_id,
        "thread_id": email.thread_id,
        "subject": email.subject,
        "sender": str(email.sender.email),  # Adjust if needed
        "to": request.user.email,
        "body": email.body,
        "snippet": email.snippet,
        "internal_date": email.internal_date.isoformat(),
        "label_ids": email.label_ids,
        "headers": email.headers,
        
    }
    
def trash_gmail_message(user, message_id):
    access_token = get_valid_access_token(user)
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/trash"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Message moved to trash.")
        return True
    else:
        print("Failed to trash message:", response.status_code, response.text)
        return False

    
