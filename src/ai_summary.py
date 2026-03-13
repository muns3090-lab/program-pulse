"""
AI-generated summaries for Program Pulse.
Generates structured escalation summaries and assignee nudge context
using Claude, based on JIRA ticket data and latest comments.
"""

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()


def generate_escalation_summary(at_risk_tickets: list[dict]) -> str:
    """
    Generates a structured leadership escalation summary.

    Format:
        Quick Summary
        Current Blockers
        What Is Needed
        Business Value If Not Done
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    tickets_text = "\n\n".join([
        f"Ticket: {t['key']}\n"
        f"Summary: {t['summary']}\n"
        f"Assignee: {t['assignee']}\n"
        f"Days Overdue: {t['days_overdue']}\n"
        f"Priority: {t.get('priority', 'Unknown')}\n"
        f"Last Comment: {t.get('last_comment_text', 'No comments on this ticket')}\n"
        f"Description: {t.get('description', 'No description available')[:400]}"
        for t in at_risk_tickets
    ])

    prompt = f"""You are a Technical Program Manager writing a concise escalation summary for engineering and business leadership.

The following JIRA epics/stories are overdue with no status updates from the assigned teams:

{tickets_text}

Write a structured escalation summary using EXACTLY these four sections with these exact headings:

**Quick Summary**
2-3 sentences. What work is at risk, which teams are impacted, and how long it has been delayed.

**Current Blockers**
Bullet points. Based on the ticket descriptions and last comments, list the most likely reasons for the delay. Be specific — mention technical dependencies, missing approvals, resource constraints, or unclear ownership where visible.

**What Is Needed**
Bullet points. Specific asks of leadership — unblocking actions, decisions, resource allocations, or escalations needed. Each bullet should be actionable.

**Business Value If Not Done**
2-3 sentences. What is the business or operational risk if these items remain unresolved. Connect to delivery timelines, compliance, user impact, or cost where relevant.

Write in professional, direct language. Avoid filler phrases. Do not invent facts not present in the ticket data."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_overdue_context(ticket: dict) -> str:
    """
    Generates a short AI-written context blurb for the assignee follow-up email.
    Reminds the assignee what the ticket is about and why an update matters.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""You are helping a Technical Program Manager send a nudge email to a ticket assignee.

Ticket details:
- Key: {ticket['key']}
- Summary: {ticket['summary']}
- Days Overdue: {ticket['days_overdue']}
- Description: {ticket.get('description', 'No description')[:300]}
- Last Comment: {ticket.get('last_comment_text', 'No comments yet')}

Write 2 short sentences (max 40 words total) that:
1. Briefly remind the assignee what this ticket is about in plain English
2. Note why it matters to the broader program right now

Do not start with "I". Do not use the word "important". Keep it factual and direct."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text