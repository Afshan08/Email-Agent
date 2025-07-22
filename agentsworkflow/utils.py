from typing import Optional


from agents import (
    Agent,
    InputGuardrail,
    AsyncOpenAI,
    Runner,
    GuardrailFunctionOutput,
    OpenAIChatCompletionsModel,
    InputGuardrailTripwireTriggered,
    function_tool,
    RunContextWrapper,
    RunHooks,
    AgentHooks
)
from itertools import islice
from uuid import UUID
from agents.run import RunConfig
from pydantic import BaseModel
from agents import set_default_openai_client
from datetime import datetime
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
import json
from asgiref.sync import sync_to_async
import asyncio
from openai import OpenAI
from typing import List
import sys
import os
from dotenv import load_dotenv
load_dotenv()

from asgiref.sync import sync_to_async
from dataclasses import dataclass
from agents.result import RunResultBase
from .email_manager_agent_instructions import Instructions


instructions_for_manager_agent = Instructions()
# Gemini API key
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your environment variables.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)


client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)



def get_data(id, django_model):
    return django_model.objects.get(id=id)

def batchify(iterable, batch_size):
    """Yield successive batch_size chunks from iterable."""
    iterable = iter(iterable)
    while True:
        batch = list(islice(iterable, batch_size))
        if not batch:
            break
        yield batch





class EmailContext(BaseModel):
    """
    A class representing structured email data passed to or from the Agent.

    Schema:
    {
        "uuid": "UUID of the email",
        "sender": "Sender's name or email address",
        "receiver": "Receiver's name or email address",
        "subject": "Subject line of the email",
        "body": "Body/content of the email",
        "timestamp": "Timestamp of when the email was received",
        "is_read": "Boolean flag if email has been read",
        "should_reply": "Boolean flag if email needs a reply",
        "is_replied": "Boolean flag if email has already been replied to",
        "can_llm_reply": "Boolean flag if LLM is allowed to reply",
        "category": "Category of the email such as 'marketing', 'social', 'work', etc."
    }
    """
    uuid: UUID
    sender: str
    receiver: str
    subject: str
    body: str
    timestamp: datetime
    is_read: bool
    should_reply: bool
    is_replied: bool
    can_llm_reply: bool
    category: str

    
class ThirtyMailsContext(BaseModel):
    context: List[EmailContext]



class EmailReply(BaseModel):
    uuid: UUID
    sender: str
    receiver: str
    subject: str
    body: str
    timestamp: datetime
    is_read: bool
    should_reply: bool
    is_replied: bool 
    category: str
    reply: str


    model_config = {
        "extra": "forbid"  # ✅ Pydantic v2 way
    }
    

@sync_to_async
def data_parser(mail):
    return [
        EmailContext(
            uuid=email.uuid,
            sender=email.sender.name,
            receiver=email.reciver.username,
            subject=email.subject,
            body=email.body,
            timestamp=email.timestamp,
            is_read=email.is_read,
            should_reply=email.should_reply,
            is_replied=email.is_replied,
            can_llm_reply=False,
            category=email.category if email.category else "not categorized",
        )
    for email in mail]


@sync_to_async
def single_data_parser(email):
    
    return [
        EmailContext(
            uuid=email.uuid,
            sender=email.sender.name,
            receiver=email.reciver.username,
            subject=email.subject,
            body=email.body,
            timestamp=email.timestamp,
            is_read=email.is_read,
            should_reply=email.should_reply,
            is_replied=email.is_replied,
            can_llm_reply=False,
            category=email.category,
        )
    ]



from pydantic import BaseModel

@function_tool
async def update_email_context(ctx: RunContextWrapper[EmailContext], new_context: EmailContext) -> str:
    """This function updates the email context with new information.
    by using the EmailContext object that comes from updates variable.
    It returns a success message."""

    ctx.context = new_context
    
     # Update the context with new information
    return (f"""The email is from {ctx.context.sender} to {ctx.context.receiver} with subject {ctx.context.subject}\n\nand body {ctx.context.body} \n\n
Here is is replied is {ctx.context.is_replied} and category is {ctx.context.category} at timestamp {ctx.context.timestamp}
and is uniquely indentifies by its uuid that is {ctx.context.uuid}""")


@function_tool
async def get_email_context(ctx: RunContextWrapper[EmailContext]) -> str:
    """ This Function returns the context in the form of string about emails provided in 
    the context as string"""
    return (f"""The email is from {ctx.context.sender} to {ctx.context.receiver} with subject {ctx.context.subject}\n\nand body {ctx.context.body} \n\n
Here is is replied is {ctx.context.is_replied} and category is {ctx.context.category} at timestamp {ctx.context.timestamp}
and is uniquely indentifies by its uuid that is {ctx.context.uuid}""")
    

@function_tool
async def get_thirty_email_context(ctx: RunContextWrapper[ThirtyMailsContext]) -> str:
    """ This Function returns the context in the form of string about emails provided in 
    the context as string"""
    data = []
    print("TOOL WAS CALLED:")
    for i in range(len(ctx.context)):
        
        data.append (f"""The email is from {ctx.context[i].sender} to {ctx.context[i].receiver} with subject {ctx.context[i].subject}\n\nand body {ctx.context[i].body} \n\n
    Here is is replied is {ctx.context[i].is_replied} and category is {ctx.context[i].category} at timestamp {ctx.context[i].timestamp}
    and is uniquely indentifies by its uuid that is {ctx.context[i].uuid}""")
    return data

email_reply_writer_agent = Agent[EmailContext](
    model=model,
    name="email_reply_writer_agent",
    instructions="""
You are a specialized agent that writes professional and appropriate email replies.

You must always start by calling the `get_email_context` tool to retrieve the latest context about the email. This ensures you're using up-to-date information.

You must not make assumptions. Always rely on tool output.

Your only task is to return a valid `EmailReply` object. You are not allowed to modify the context directly.

How to proceed:
- Call `get_email_context` to understand the email (call it again if you're unsure).
- Use the returned string to write a relevant, polite, and clear reply.
- If the email doesn't deserve a reply (e.g., spam or notification), return `EmailReply(reply=None)`.

Return only an instance of `EmailReply` as your output. Do not include anything else. and keep all of the other things same like 
timestamp and subject and body from the context just the reply key and the is_replied change thte is_replied to true once you generate a reply.
the EmailReply has these attributes:
    uuid: uuid
    sender: str
    receiver: str
    subject: str
    body: str
    timestamp: datetime
    is_read: bool (Change this to true)
    should_reply: bool
    is_replied: bool (Change this to true)
    category: str 
    reply: str
""",
    tools=[get_email_context],
    handoff_description="This agent writes replies to emails based on their content.",
    output_type=EmailReply,
)



email_manager_agent = Agent[EmailContext](
    model=model,
    name="email_manager_agent",
    instructions=instructions_for_manager_agent.instructions,
    tools=[get_email_context, update_email_context],
    handoffs=[email_reply_writer_agent],
)


@function_tool
def get_time():
    "Returns current date so that the agent knows what are the mails that are for today."
    return datetime.now()

email_chat_agent = Agent[ThirtyMailsContext](
    model=model,
    name="email_chat_agent",
    instructions="""
        You are an email chat agent designed to answer questions based on the user's last 30 emails.

        You have access to a tool called `get_thirty_email_context`, which will provide the necessary context. You do not need to worry about how arguments are passed — that is handled automatically by the system.
        also if the user asks for todays mails so first call the get time and than give the mails that are of today. The get time function gives
        you todays date and time and you just have to emphasize on the date. and also have a proper format for return instead of just returning so badly formatted text and so much un
        wanted information. Use html tags like </br> and others for nice formatting.
        Only answer questions using the provided email context. If the question cannot be answered using this context, respond with the answer or the error from the tool:
        
        """,
    tools=[get_thirty_email_context, get_time],
    output_type=str,
)


            
            