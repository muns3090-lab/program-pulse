#!/usr/bin/env python3
"""
Program Pulse — autonomous program health agent.

Usage:
    python main.py          # live mode (requires config.yaml + .env)
    python main.py --demo   # demo mode (no credentials needed)
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()


def run_live():
    from src.config_loader import load_config
    from src.jira_client import JiraClient
    from src.confluence_client import ConfluenceClient
    from src.notifier import Notifier
    from src.scheduler import classify_tickets
    from src.ai_summary import generate_escalation_summary, generate_overdue_context
    from src.escalation_state import (
        was_escalated_recently,
        mark_escalated,
        clear_resolved_tickets
    )
    from datetime import date

    print("🚀 Program Pulse — live mode")
    config = load_config()

    jira = JiraClient(config)
    confluence = ConfluenceClient(config)
    notifier = Notifier(config)

    cooldown_days = config.get("schedule", {}).get("escalation_cooldown_days", 7)

    print("📡 Fetching tickets from JIRA...")
    issues = jira.get_epics_and_stories()
    print(f"   Found {len(issues)} epics/stories with due dates")

    due_today, needs_follow_up, at_risk = classify_tickets(
        issues, jira.get_last_comment_date
    )

    # ── 1. Due today reminders ────────────────────────────────────────
    print(f"\n📌 Due today: {len(due_today)} tickets")
    for t in due_today:
        if t["assignee_email"]:
            ticket_url = f"{config['jira']['base_url']}/browse/{t['key']}"
            notifier.send_due_today(
                to_email=t["assignee_email"],
                assignee_name=t["assignee"],
                ticket_key=t["key"],
                ticket_summary=t["summary"],
                due_date=t["due_date"],
                ticket_url=ticket_url
            )

    # ── 2. Overdue follow-ups — ask for structured comment ────────────
    print(f"\n⏰ Needs follow-up: {len(needs_follow_up)} tickets")
    for t in needs_follow_up:
        if t["assignee_email"]:
            ticket_url = f"{config['jira']['base_url']}/browse/{t['key']}"
            # Enrich with last comment text for AI context
            t["last_comment_text"] = jira.get_last_comment_text(t["key"])
            ai_context = generate_overdue_context(t)
            notifier.send_follow_up(
                to_email=t["assignee_email"],
                assignee_name=t["assignee"],
                ticket_key=t["key"],
                ticket_summary=t["summary"],
                days_overdue=t["days_overdue"],
                ticket_url=ticket_url,
                ai_context=ai_context
            )

    # ── 3. Escalations — 7-day cooldown per ticket ───────────────────
    print(f"\n⚠️  At risk: {len(at_risk)} tickets")

    tickets_to_escalate = []
    tickets_skipped = []

    for t in at_risk:
        t["last_comment_text"] = jira.get_last_comment_text(t["key"])
        if was_escalated_recently(t["key"], cooldown_days=cooldown_days):
            tickets_skipped.append(t)
            print(f"   ⏭ Skipping {t['key']} — escalation sent within last {cooldown_days} days")
        else:
            tickets_to_escalate.append(t)

    if tickets_skipped:
        print(f"   {len(tickets_skipped)} ticket(s) skipped (within cooldown window)")

    if tickets_to_escalate:
        print(f"   Escalating {len(tickets_to_escalate)} ticket(s)...")
        print("🤖 Generating AI escalation summary...")
        summary = generate_escalation_summary(tickets_to_escalate)

        escalate_formatted = [{
            **t,
            "url": f"{config['jira']['base_url']}/browse/{t['key']}"
        } for t in tickets_to_escalate]

        notifier.send_escalation(summary, escalate_formatted)

        for t in tickets_to_escalate:
            jira.add_label(t["key"], config["jira"]["at_risk_label"])
            jira.add_comment(
                t["key"],
                f"🚨 Program Pulse: This item is {t['days_overdue']} days overdue "
                f"with no update. Escalation sent to leadership. "
                f"Next reminder: 7 days."
            )
            mark_escalated(t["key"])

        # Update Confluence status page
        today = date.today()
        epics_summary = []
        for issue in issues:
            f = issue["fields"]
            due_str = f.get("duedate")
            if not due_str:
                continue
            from datetime import date as dt
            due = dt.fromisoformat(due_str)
            days = (today - due).days
            status = "Overdue" if days >= 2 else "At Risk" if days == 1 else "On Track"
            epics_summary.append({
                "key": issue["key"],
                "summary": f["summary"],
                "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                "due_date": due_str,
                "status": status,
            })
        confluence.update_status_page(epics_summary)
        print("✅ Confluence status page updated")
    else:
        print("   No new escalations needed today")

    print("\n✅ Program Pulse run complete")


def run_demo():
    from demo.demo_runner import run_demo as demo
    demo()


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_live()