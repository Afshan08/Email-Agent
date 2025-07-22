from django.shortcuts import render, redirect, get_object_or_404, reverse
from .utils import get_data, email_manager_agent, email_reply_writer_agent, data_parser
from .models import IncomingEmails
from django.contrib.auth.models import User as Users
from django.core.paginator import Paginator
from agents import Runner
import asyncio
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.http import HttpResponse
from openai import RateLimitError
from agentsworkflow.utils import EmailReply
from .utils import batchify

# Create your views here.


def index(request):
    return render(request, 'agentsworkflow/index.html')


def fetch_emails(request, id):
    user = get_object_or_404(Users, id=id)
    data = get_data(id=id, django_model=Users)
    email_list = IncomingEmails.objects.filter(reciver=user).order_by('-timestamp')
    
    # setting up the paginator:
    paginator = Paginator(email_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'agentsworkflow/fetching_data.html', {
        'page_obj': page_obj,
    })
    


def process_emails(request, id):
    user = get_object_or_404(Users, id=id)
    email_list = IncomingEmails.objects.filter(reciver=user).order_by('-timestamp')


    async def run_emails(ctx):
        for batch in batchify(ctx, 3):
            tasks = []
            for email in batch:
                tasks.append(process_single_email(email))
            await asyncio.gather(*tasks)
            await asyncio.sleep(120)
    


    @sync_to_async
    def save_email_transaction(email_reply):
        try:
            reciver = Users.objects.get(username=email_reply.sender)
            sender = Users.objects.get(username=email_reply.receiver)

            email = IncomingEmails.objects.filter(uuid=email_reply.uuid, is_replied=False, is_read=False).first()
            if email:
                email.is_read = email_reply.is_read
                email.is_replied = email_reply.is_replied
                email.category = email_reply.category
                email.save()

            if email_reply.reply:
                IncomingEmails.objects.create(
                    sender=sender,
                    reciver=reciver,
                    subject=f"Re: {email_reply.subject}",
                    body=email_reply.reply,
                    timestamp=timezone.now(),
                    is_read=False,
                    should_reply=False,
                    is_replied=False,
                    category=email_reply.category,
                    reply_to=email
                )
        except Users.DoesNotExist:
            return "User does not exist"

    
    async def process_single_email(email):

        try:
            result = await Runner.run(
                email_manager_agent,
                input="Categorize the emails and reply them if necessary.",
                context=email,
                max_turns=30
            )
                        
            print("🧪 result.final_output =", result.final_output)
            print("✅ type =", type(result.final_output)) 
            if not isinstance(result.final_output, EmailReply):
                print("Type was wrong")
                return
            else:
                email_reply = result.final_output
                await save_email_transaction(email_reply)
        except Exception as e:
            print(f"Error processing email: {e}")

    
    
    ctx = data_parser(email_list)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_emails(ctx))
    loop.close()
    
            

        
    context = {
        "email_list": email_list,
    }
    
    if request.headers.get("HX-Request") == "true":
        html = render_to_string("agentsworkflow/processing_emails.html", context)
        return HttpResponse(html)

    return render(request, "agentsworkflow/processed_emails.html", context)


