SYSTEM_PROMPT = """
You are an AI assistant that writes concise, professional outreach emails.

Rules:
- Be short and clear
- Do not exaggerate
- Do not invent facts
- Do not sound salesy
- Output plain text only
"""

SUBJECT_PROMPT = """
Create a concise, professional email subject line for the role:
{role}

Guidelines:
- Max 10 words
- Clear intent
- No emojis
"""

BODY_PROMPT = """
Write a short professional email introduction (4–6 lines).

Candidate name:
{name}

Target role:
{role}

Portfolio summary:
{portfolio_summary}

Guidelines:
- Confident but humble
- Clear value
- No fluff
- Only one role
"""

REFINE_PROMPT = """
Improve the following email while keeping it:
- Short
- Professional
- Human
- Clear
- Not mentioning different roles only one role for whole body

Email:
\"\"\"
{email}
\"\"\"
"""

EMAIL_RULES = [
    {
        "name": "subject_length",
        "check": lambda subject, body: len(subject) <= 120
    },
    {
        "name": "body_length",
        "check": lambda subject, body: 50 <= len(body) <= 1200
    },
    {
        "name": "no_placeholders",
        "check": lambda subject, body: "{" not in body and "}" not in body
    }
]

def build_subject_prompt(role):
    return SUBJECT_PROMPT.format(role=role)

def build_body_prompt(name, role, portfolio_summary):
    return BODY_PROMPT.format(
        name=name,
        role=role,
        portfolio_summary=portfolio_summary
    )

def build_refine_prompt(email_text):
    return REFINE_PROMPT.format(email=email_text)

def validate_email(subject, body):
    failed = []

    for rule in EMAIL_RULES:
        if not rule["check"](subject, body):
            failed.append(rule["name"])

    return len(failed) == 0, failed