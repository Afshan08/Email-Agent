"""
The tool is about categorizing emails into certain categories I have these emails
in a file first I will open them and then parse them in the memory and then
giving it to the function one by one first function is opening the file
"""

import json
from typing import List
import os
import re
from pydantic import BaseModel
from openai import OpenAI
from ...models import IncomingEmails, OutgoingMails, Users

gemini_api_key = 'AIzaSyAGSZX3bOq1ReFB3CzDZJMqrFkglozErP8'  # Replace with your actual Gemini API key

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class User(BaseModel):
    username: str
    emailaddress: str


class IncomingEmail(BaseModel):
    user : User
    subject : str
    body : str
    timestamp: str
    is_read:  bool
    should_reply:  bool
    is_replied : bool
    category : str 




def retrive_data(user_name):
    user_data = Users.objects.get(username=user_name)
    user_mails = IncomingEmails.objects.filter(user__username=user_name)
    outgoing_mails = OutgoingMails.objects.filter(user__username=user_name)
    return [user_data, user_mails, outgoing_mails]
    

def individual_emails(user_mails):
    return [mail for mail in user_mails]

    
    
def update_database(name_of_model, data):
    """
    Updates a database table by adding new_data as the model object to the existing database
    table
    """
    try:
        instance = name_of_model.objects.create(**data)
    except Exception as e:
        print(f"Failed to insert into {name_of_model.__name__}: {e}")
        return None
    return instance
    
    
def parse_emails_from_database(model_name: str) -> List[IncomingEmail]:
    """
    Reads a data entries and parses it into a list of Email objects.

    Args:
        file_name (str): Path to the JSON file.

    Returns:
        List[Email]: A list of parsed Email objects.
    """
    raw_data = model_name.objects.all()
    email_objects = []

    for email in raw_data:
        try:
            email_obj = IncomingEmail(
                            user=User(
                                username=email.user.username,
                                emailaddress=email.user.emailaddress
                            ),
                            subject=email.subject,
                            body=email.body,
                            timestamp=str(email.timestamp),
                            is_read=email.is_read,
                            should_reply=email.should_reply,
                            is_replied=email.is_replied,
                            category=email.category or "Uncategorized"
                        )
            email_objects.append(email_obj)
        except KeyError as e:
            print(f"Skipping email due to missing key: {e}")
            continue

    return email_objects


def categorize_emails(emails: List[IncomingEmail]) -> List[IncomingEmail]:
    email_descriptions = "\n\n".join([
        f"Email {i+1}:\nSubject: {e.subject}\nBody: {e.body}\nSender: {e.user.emailaddress} and timestamp: {e.timestamp}" 
        for i, e in enumerate(emails)
    ])

    prompt = f"""
You are an intelligent email categorizer. Categorize each of the following emails into one of:
- marketing
- personal
- social
- news
- career
- education
- security
- other

Return the result as a JSON array of objects with these keys:
    user : User
    subject : str
    body : str
    timestamp: str
    is_read:  bool
    should_reply:  bool
    is_replied : bool
    category : str 

Some are already given to you and the boolean values you do not know should be False.

Emails:
{email_descriptions}
"""

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who categorizes emails."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    reply_content = response.choices[0].message.content.strip()
    print("LLM Response:\n", reply_content)

    try:
        if reply_content.startswith("```json"):
            reply_content = re.sub(r"^```json\s*|\s*```$", "", reply_content.strip())
        categorized_raw = json.loads(reply_content)
    except json.JSONDecodeError:
        raise ValueError("LLM response is not valid JSON.")

    categorized_emails = []
    for email in categorized_raw:  
        try:
            email_obj = IncomingEmail.model_validate(email)
            update_database(IncomingEmails, email_obj.dict())

            categorized_emails.append(email_obj)
            

        except Exception as e:
            print(f"Skipping bad email: {email} — Error: {e}")
            continue
