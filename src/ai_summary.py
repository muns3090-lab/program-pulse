import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


def generate_escalation_summary(at_risk_tickets):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    tickets_text = "\n".join([
        f"- {t['key']}: {t['summary']} | Assignee: {t['assignee']} | "
        f"{t['days_overdue']} days overdue | Last comment: {t.get('last_comment', 'None')} | "
        f"Description: {t.get('description', 'No description')[:300]}"
        for t in at_risk_tickets
    ])

    prompt = f"""You are a Technical Program Manager writing a concise escalation summary for engineering leadership.

The following JIRA epics/stories are overdue with no status updates:

{tickets_text}

Write a plain-English escalation summary (3-4 sentences) that includes:
1. What is at risk (what work, which teams)
2. Why it appears delayed based on the ticket context
3. What help or unblocking action is needed from leadership
4. The business impact if not resolved

Write in professional but direct language. No bullet points — write in paragraph form.
Do not start with "I" and do not use filler phrases like "It is important to note"."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text