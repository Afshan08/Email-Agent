from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import login, logout, authenticate, user_logged_in
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .query import QueryForm
import traceback
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.contrib.auth.models import User as Users
from django.core.paginator import Paginator
import markdown
from django.utils.safestring import mark_safe
from markdown import markdown as md_to_html
from authentication.utils import get_gmail_messages, gmail_message, extract_email_details, clean_email_body
from authentication.utils import get_gmail_history, send_gmail_email, extract_email_details_from_model
from authentication.utils import reply_to_gmail_email, trash_gmail_message

from agentsworkflow.models import IncomingEmails, GmailContact, GmailSyncState
from email.utils import parseaddr
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 
import json
import asyncio

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from agentsworkflow.models import IncomingEmails

from agentsworkflow.utils import email_manager_agent, email_chat_agent
from agentsworkflow.utils import data_parser, batchify
from asgiref.sync import sync_to_async
import asyncio

from agentsworkflow.utils import batchify
from agentsworkflow.utils import EmailReply
from agentsworkflow.utils import data_parser, single_data_parser

from agents import Runner

from asgiref.sync import async_to_sync
from .forms import AgentReplyForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from asgiref.sync import sync_to_async

User = get_user_model()



def send_test_email(user):
    send_gmail_email(user, "afridiafshan01@gmail.com", "Test Email", "This is a test email.")


def handle_incremental_sync(user, sync_state):
    final_data = []
    raw_data = []
    history_data = get_gmail_history(user, sync_state=sync_state)
    history = history_data.get("history", [])

    for change in history:
        messages_added = change.get("messagesAdded", [])
        for msg_entry in messages_added:
            msg_id = msg_entry["message"]["id"]
            full_msg, extracted = fetch_and_parse_message(msg_id, user)
            if not full_msg or email_exists(extracted["message_id"]):
                continue

            contact = get_or_create_contact(extracted["sender"])
            save_email(user, contact, extracted)
            final_data.append(extracted)
            raw_data.append(full_msg)

    new_history_id = history_data.get("historyId")
    if new_history_id:
        sync_state.history_id = new_history_id
        sync_state.save()

    return final_data, raw_data


def handle_initial_sync(user):
    final_data = []
    raw_data = []
    message_data = get_gmail_messages(user)
    for message in message_data.get("messages", []):
        msg_id = message.get("id")
        full_msg, extracted = fetch_and_parse_message(msg_id, user)
        if not full_msg or email_exists(extracted["message_id"]):
            continue

        contact = get_or_create_contact(extracted["sender"])
        save_email(user, contact, extracted)
        final_data.append(extracted)
        raw_data.append(full_msg)

    if final_data:
        last_history_id = final_data[-1].get("history_id")
        if last_history_id:
            GmailSyncState.objects.update_or_create(user=user, defaults={"history_id": last_history_id})

    return final_data, raw_data


def fetch_and_parse_message(msg_id, user):
    full_msg = gmail_message(msg_id, user)
    if not full_msg:
        return None, None
    extracted = extract_email_details(full_msg)
    return full_msg, extracted


def get_or_create_contact(sender_header):
    sender_name, sender_email = parseaddr(sender_header)
    contact, _ = GmailContact.objects.get_or_create(
        email=sender_email,
        defaults={"name": sender_name}
    )
    return contact


def email_exists(message_id):
    return IncomingEmails.objects.filter(message_id=message_id).exists()


from django.db import transaction

def save_email(user, contact, extracted):
    # Use update_or_create to avoid duplicates and simplify logic
    IncomingEmails.objects.update_or_create(
        message_id=extracted["message_id"],
        defaults={
            "sender": contact,
            "reciver": user,
            "subject": extracted["subject"],
            "body": extracted["body"],
            "snippet": extracted["snippet"],
            "timestamp": now(),
            "internal_date": extracted["internal_date"],
            "thread_id": extracted["thread_id"],
            "in_reply_to": extracted.get("in_reply_to", ""),
            "label_ids": extracted.get("label_ids", []),
            "headers": extracted.get("headers", {}),
        }
    )


@login_required
def home_page(request):
    user = request.user
    final_data = []
    raw_data = []

    sync_state = GmailSyncState.objects.filter(user=user).first()
    try:  
        if sync_state and sync_state.history_id:
            final_data, raw_data = handle_incremental_sync(user, sync_state)
            
        else:
            final_data, raw_data = handle_initial_sync(user)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    return redirect('get_inbox')


## Making some useful API's in the views

# TODO: Add a route for getting a mail with message_id and user get a json response
@login_required
def get_mail(request, message_id, user_id):
    """
    API to get a specific mail with message_id

    Args:
        message_id (str): The message_id of the mail to retrieve
        user_id (int): The id of the user to retrieve the mail for

    Returns:
        JsonResponse: A JSON response containing the mail details
    """
    if request.user.id != user_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    user = get_object_or_404(User, id=user_id)
    
    email_obj = IncomingEmails.objects.filter(message_id=message_id, reciver=user).first()
    if email_obj:
        email_obj = extract_email_details_from_model(request, email_obj)
        return JsonResponse(data)
    # Fallback gettig the message from gmail servers
    
        # If the message is not present in the database, fetch it from Gmail
    api_data = gmail_message(message_id, user)
    if not api_data:
        return JsonResponse({"error": "Mail not found"}, status=404)
    data = extract_email_details(api_data)
    return JsonResponse(data)


# TODO: Add a route to send mails with with adding parameters:

@csrf_exempt
@login_required
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        to = data.get("to")
        subject = data.get("subject")
        body_text = data.get("body", "")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid Json payload."}, status=400)
    
    if not to or not body_text:
        return JsonResponse({"error": "Missing required fields"}, status=400)
    
    status = send_gmail_email(request.user, to, subject, body_text)
    if status:
        reciver, _ = GmailContact.objects.get_or_create(
                        email=to,
                        defaults={"name": to.split("@")[0]}
                )

    
        sent_msg_id = status.get("id")
        thread_id = status.get("threadId")
        message = IncomingEmails.objects.create(
            is_read=True,
            reciver=reciver,  # or leave blank
            sender=request.user,
            subject=subject,
            body=body_text,
            message_id=sent_msg_id,
            thread_id=thread_id,
            timestamp=now(),
            reply_to=None,
            is_outgoing=True,
            is_reply_generated_by_agent=True,
            sent=True,
            reviewed=True, 
        )
        return JsonResponse({"message": "Mail sent and saved successfully."})
        
    
    else:
        return JsonResponse({"error": "Failed to send email"}, status=500)
    
    

@csrf_exempt
@login_required
@require_POST
def reply_to_mails(request, message_id, thread_id):  
    """API to reply to an existing email thread.\
    """ 
    print("message_id:", message_id, "thread_id:", thread_id)
    try:
        reply = IncomingEmails.objects.get(reply_to__message_id=message_id, is_outgoing=True)
        original_email = IncomingEmails.objects.filter(message_id=message_id).first()
        
        to = original_email.sender.email if original_email else None
        subject = reply.subject
        body_text = reply.body
        print("GOT BODY TEXT:", body_text)
    except IncomingEmails.DoesNotExist:
        return JsonResponse({"error": "No reviewed reply found for this message."}, status=404)
    status = reply_to_gmail_email(request.user, to, subject, body_text, thread_id, message_id)
    if status:
        reciver, _ = GmailContact.objects.get_or_create(
            email=to,
            defaults={"name": to.split("@")[0]}
        )
        reply_target = IncomingEmails.objects.filter(message_id=message_id).first()
    
        sent_msg_id = status.get("id")
        threadid = status.get("threadId")
       
        with transaction.atomic():
            IncomingEmails.objects.filter(id=reply.id).update(
                message_id=sent_msg_id,
                thread_id=threadid,
                sent=True,
            )
        return JsonResponse({"message": "Reply sent and saved successfully."})

    else:
        return JsonResponse({"error": "Failed to reply to email"}, status=500)
    
    
    
# ----------------------------------------------------------------
# ----------------------------------------------------------------

# Views connected with templates:


def load_inbox(request):
    user = request.user
    gmail_contact = GmailContact.objects.filter(email=user.email).first()

    email_list = IncomingEmails.objects.filter(reciver=user, is_outgoing=False).order_by('-internal_date')
    sent_email = IncomingEmails.objects.filter(sender=gmail_contact, is_outgoing=True).order_by('-internal_date')

    # Pagination setup
    paginator = Paginator(email_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'get_mails.html', {
        'page_obj': page_obj,
        'sent_mails': sent_email
    })

    
    
def get_indivisual_mail(request, message_id):
    
    mail = IncomingEmails.objects.filter(id=message_id).first()
    # replies = IncomingEmails.objects.filter(reply_to=mail).first()
    # print(replies.body)

    return render(request, "get_indivisual_mail.html", {
        "mail": mail, 
        # "replies": replies
    })
 

@login_required
def get_replies(request):
    user = request.user
    users_contact = GmailContact.objects.filter(email=user.email).first()
    agent_generated_replies = IncomingEmails.objects.filter(
    sender=users_contact,
    is_reply_generated_by_agent=True,
    is_outgoing=True,
    reply_to__isnull=False
)
    return render(request, "get_replies.html", {
        "replies": agent_generated_replies,
    })
    

@login_required
def delete_sent_mails(request, message_id):
    user = request.user
    email = get_object_or_404(IncomingEmails, message_id=message_id)
    # sender_contact = GmailContact.objects.filter(email=user.email).first()
    if email.sender.email != user.email:
        return HttpResponseForbidden("You are not allowed to delete this email.")

    if email.message_id:
        trash_gmail_message(user, email.message_id)  # Gmail API call
    email.is_deleted_by_sender = True  # Optional: App-side tracking
    email.save()

    return redirect("get_replies")


## These are the functions and agents that would be used in the future views.

@sync_to_async
def save_email_transaction(user_id, email_reply):
    try:
        user = User.objects.get(id=user_id)  # Use get() instead of filter().first()
        
        # Get receiver contact (the original sender)
        receiver_contact, _ = GmailContact.objects.get_or_create(
            email=email_reply.sender,
            defaults={"name": email_reply.sender.split("@")[0]}
        )

        # Update the ORIGINAL email
        original_email = IncomingEmails.objects.filter(
            uuid=email_reply.uuid).first()

        
        if original_email:
            with transaction.atomic():
                original_email.is_read = True
                original_email.is_replied = email_reply.is_replied
                original_email.category = email_reply.category
                original_email.save()
        already_replied = IncomingEmails.objects.filter(
            reply_to=original_email,
            is_outgoing=True,
            is_reply_generated_by_agent=True
        ).exists()
        if already_replied:
            print(f"↪️ Reply already exists for email {original_email.uuid}. Skipping creation.")
            return None

        # Create the REPLY email (outgoing)
        if email_reply.reply:
            sender_contact, _ = GmailContact.objects.get_or_create(
                email=user.email,
                defaults={"name": user.username}
            )
            IncomingEmails.objects.create(
                sender=sender_contact,
                reciver=user,  
                subject=f"Re: {email_reply.subject}",
                body=email_reply.reply,
                timestamp=timezone.now(),
                internal_date=timezone.now(),
                is_read=False,
                should_reply=False,
                is_replied=False,
                category=email_reply.category,
                in_reply_to=original_email.id,
                is_outgoing=True,
                is_reply_generated_by_agent=True,
                sent=False,
                reviewed=False,
                reply_to=original_email,
            )
            print(original_email)
    except Exception as e:
        print(f"Error saving email transaction: {e}")



async def process_single_email(user, email_id):
    try:
        @sync_to_async
        def get_email_object(email_id):
            return IncomingEmails.objects.get(id=email_id)

        email_obj = await get_email_object(email_id)
        email_context = await single_data_parser(email_obj)
        print(email_context[0].category)
        print(f"email_subject: {email_context[0].subject}")
        if not email_context:
            print("no email context")
        result = await Runner.run(
            email_manager_agent,
            input="Categorize the emails and reply them if necessary.",
            context=email_context[0],
            max_turns=30
        )

        if isinstance(result.final_output, EmailReply):
            print("✅ Valid output type")
            print(result.final_output)
            await save_email_transaction(user, result.final_output)
            return result.final_output
        else:
            print("❌ Invalid output type")
            print(result.final_output)
            return result.final_output
    except Exception as e:
        print(f"Error processing email in agents output: {e}")




# Review view:

from django.db import transaction

@csrf_protect
@login_required
async def review_agents_response(request, message_id):

    user = await sync_to_async(get_user)(request)
    user_id = user.id

    email = await sync_to_async(get_object_or_404)(
        IncomingEmails.objects.select_related('sender', 'reciver'),
        id=message_id
    )
    reciver_id = email.reciver.id

    reply_email = await sync_to_async(
        lambda: IncomingEmails.objects.filter(
            reply_to=message_id,
            is_outgoing=True,
            is_reply_generated_by_agent=True
        ).first()
    )()

    if reciver_id != user_id:
        return await sync_to_async(render)(request, "error.html", {"message": "Unauthorized access."})


    if request.method == "POST":
        form = AgentReplyForm(request.POST)
        if form.is_valid():
            response_text = form.cleaned_data["response"]
            if reply_email:
                @sync_to_async
                def update_reply_email(reply_email, response_text):
                    with transaction.atomic():
                        reply_email.body = response_text
                        reply_email.reviewed = True
                        reply_email.is_replied = False
                        reply_email.save()

                await update_reply_email(reply_email, response_text)
            else:
                sender, _ = await sync_to_async(GmailContact.objects.get_or_create)(
                    email=request.user.email,
                    defaults={"name": request.user.username}
                )
                await sync_to_async(IncomingEmails.objects.create)(
                    sender=sender,
                    reciver=request.user,
                    subject=f"Re: {email.subject}",
                    body=response_text,
                    timestamp=timezone.now(),
                    internal_date=timezone.now(),
                    is_read=False,
                    should_reply=False,
                    is_replied=False,
                    category=email.category,
                    in_reply_to=email.message_id,
                    is_outgoing=True,
                    is_reply_generated_by_agent=True,
                    sent=False,
                    reviewed=True,
                    reply_to=email,
                )
            return redirect("get_inbox")

    # GET request
    if reply_email:
        form = AgentReplyForm(initial={"response": reply_email.body})
        response = reply_email
    else:
        agent_response = await process_single_email(user_id, message_id)
        if not agent_response:      
            return render(request, "error.html", {"message": "Agent failed to process this email."})
        form = AgentReplyForm(initial={"response": agent_response.reply})
        response = agent_response

    return render(request, "review_agent_response.html",{
        "form": form,
        "response": response,
        "email_id": message_id,
        "original_email": email,
    })

# Some more api's:


async def chat_with_agent_on_email(user, user_query: str):
    try:
        @sync_to_async
        def get_email_object(user):
            return IncomingEmails.objects.filter(reciver=user).order_by('-internal_date')[:30]

        email_obj = await get_email_object(user)
        email_context = await data_parser(email_obj)

        result = await Runner.run(
            email_chat_agent,  # Reuse your existing agent
            input=user_query,
            context=email_context,
            max_turns=100  # Less than reply generation
        )

        return result.final_output  # string expected

    except Exception as e:
        print(f"Error in chat agent: {e}")
        return "Sorry, I couldn't understand that."
    
  
from asgiref.sync import async_to_sync
@csrf_exempt  
async def agent_chat_response(request):
    try:
        if request.method == "POST":
            query = request.POST.get("query", "")
            query = f"Server received: {query}"
            user = request.user
            answer = await chat_with_agent_on_email(user, query)
            markdown_response = md_to_html(answer)  # Convert Markdown to HTML
            safe_html = mark_safe(markdown_response)   # check if it's a coroutine
            return JsonResponse({"response": safe_html}, status=200)
    except Exception as e:
        print("Error occurred:", e)
        traceback.print_exc()
        return JsonResponse({"error": "Internal Server Error"}, status=500)
        
    return JsonResponse({"error": "Invalid request"}, status=400,)

def query_view(request):
    form = QueryForm()
    return render(request, "query_page.html", {"form": form})
