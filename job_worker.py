import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from datetime import datetime, timezone, timedelta

from concurrent.futures import ThreadPoolExecutor
from email_worker import curate_email, add_to_poc, check_mail
import sys



from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not API_ID or not API_HASH:
    API_ID = 0
else:
    API_ID = int(API_ID)

channels = [c.strip() for c in (os.getenv("CHANNEL_NAMES") or "").split(",") if c.strip()]



ROLE_KEYWORD = os.getenv("ROLE_KEYWORD", "Software Engineer")

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    if API_ID == 0:
        print("Error: API_ID is missing. Cannot initialize TelegramClient.")
        client = None
    else:
        client = TelegramClient("jobbot", API_ID, API_HASH)

executor = ThreadPoolExecutor(max_workers=3)

def extract_emails_with_context(text):
    if not text:
        return []
    
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails = re.findall(email_regex, text)
    
    unique_emails = []
    for e in emails:
        if e not in unique_emails:
            unique_emails.append(e)
            
    results = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    for email in unique_emails:
        context = ""
        for i, line in enumerate(lines):
            if email in line:
                prev = lines[i-1] if i > 0 else ""
                context = f"{prev} {line}".strip()
                break
        results.append((email, context))
    return results



async def check_and_process():
    new_count = 0
    
    await client.get_dialogs()

    for channel in channels:
        if not channel: continue
        try:
            try:
                entity = await client.get_entity(channel)
            except ValueError:
                continue

            limit = 500
            
            async for message in client.iter_messages(entity, limit=limit):
                try:
                    text = message.text or ""
                    emails_info = extract_emails_with_context(text)
                    
                    if not emails_info:
                        continue

        

                    for email, context in emails_info:
                        exists = check_mail(email)
                        if exists:
                            continue

                        role_to_use = context if context else ROLE_KEYWORD
                        
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(
                            executor,
                            add_to_poc,
                            email,
                            role_to_use
                        )
                        
                        await loop.run_in_executor(
                            executor,
                            curate_email,
                            role_to_use,
                            email
                        )
                        new_count += 1
                except Exception as e:
                    print(f"[ERROR] Error processing message")

        except Exception as e:
            print(f"[ERROR] Failed to iterate messages")


async def wait_until_9am():
    now = datetime.now()
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    
    sleep_seconds = (target - now).total_seconds()
    await asyncio.sleep(sleep_seconds)

async def start_bot(once=False):
    await client.start()
    
    if once:
        await check_and_process()
    else:
        while True:
            await wait_until_9am()
            await check_and_process()

if __name__ == "__main__":
    once = "--once" in sys.argv or os.getenv("RUN_ONCE") == "true"
    client.loop.run_until_complete(start_bot(once=once))