import os
import smtplib
import requests
import time
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

from tavily import TavilyClient
from rules import (
    SYSTEM_PROMPT,
    build_subject_prompt,
    build_body_prompt,
    build_refine_prompt,
    validate_email
)



YOUR_NAME = os.getenv("NAME")
YOUR_LINKS = (os.getenv("LINKS") or "").split(",")
BOT_KEY = os.getenv("BOT_KEY")
SCRAPE_LINKS = (os.getenv("SCRAPE_LINKS") or "").split(",")
MY_MAIL = os.getenv("MY_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RESUME_LINK = os.getenv("RESUME_LINK")

headers = {
    "User-Agent": "Mozilla/5.0"
}

tavily_client = None

def get_tavily_client():
    global tavily_client
    if tavily_client is None:
        try:
            tavily_client = TavilyClient(api_key=BOT_KEY)
        except Exception as e:
            print(f"[ERROR] Failed to initialize TavilyClient: {e}")
            return None
    return tavily_client

def search_with_retry(client, query, retries=3):
    if len(query) > 395:
        query = query[:395]
        
    for attempt in range(retries):
        try:
            return client.search(
                query=query, 
                include_answer=True
            )
        except Exception as e:
            if attempt == retries - 1:
                return None
            
            wait_time = 2 ** attempt
            time.sleep(wait_time)
            
    return None


from database import get_collection
from datetime import datetime

emails_collection = get_collection("sent_emails")
poc_collection = get_collection("point_of_contact")


def is_email_processed(recipient: str, role: str) -> bool:
    if emails_collection is None:
        return False
    return emails_collection.find_one({"recipient": recipient, "role": role}) is not None

def log_email_sent(recipient: str, role: str, subject: str):
    if emails_collection is not None:
        emails_collection.insert_one({
            "recipient": recipient,
            "role": role,
            "subject": subject,
            "sent_at": datetime.utcnow()
        })

def send_mail(subject: str, body: str, recipient: str, role: str = "Undetermined") -> bool:
    try:
        msg = EmailMessage()
        msg["From"] = MY_MAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MY_MAIL, APP_PASSWORD)
            server.send_message(msg)
        
        log_email_sent(recipient, role, subject) 
        return True
    except Exception as e:
        return False


def curate_email(role: str, recipient_email: str):
    try:
        role = (role or "").strip().replace('\n', ' ')
        
        is_invalid_role = (
            not role 
            or len(role) > 45
            or "apply" in role.lower() 
            or "link" in role.lower()
            or "click" in role.lower()
        )
        
        if is_invalid_role:
             role = "Full Stack Developer"

        if is_email_processed(recipient_email, role):
            return False

        subject_ref = f"Application for {role} - Shreevesh Kumar"

        body_ref = (
            f"Dear Hiring Team,\n\n"
            f"I am Shreevesh Kumar, writing to express my strong interest in the {role} position requesting for the 2025-2026 batch. "
            f"I have a solid technical foundation in full-stack development and a passion for building scalable web applications, and I am eager to contribute my skills to your program.\n\n"
            f"You can review my portfolio at https://shreevesh.vercel.app/ and my resume here: {RESUME_LINK}\n\n"
            f"Best regards,\n"
            f"Shreevesh Kumar"
        )

        return send_mail(subject_ref, body_ref, recipient_email, role)

    except Exception as e:
        return False


def check_mail(email):
    if emails_collection is None:
        return False
    return emails_collection.find_one({"recipient": email}) is not None

def add_to_poc(email: str, role: str):
    if poc_collection is not None:
        try:
            if not poc_collection.find_one({"email": email}):
                poc_collection.insert_one({
                    "email": email,
                    "role": role,
                    "added_at": datetime.utcnow()
                })
                return True
            else:
                return False
        except Exception as e:
            print(f"[ERROR] Failed to add to POC")
    return False