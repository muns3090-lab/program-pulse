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
    from src.ai_summary import generate_escalation_summary

    print("🚀 Program Pulse starting — live mode")
    config = load_config()

    jira = JiraClient(config)
    confluence = ConfluenceClient(config)
    notifier = Notifier(config)

    print("📡 Fetching tickets from JIRA...")
    issues = jira.get_epics_and_stories()
    print(f"   Found {len(issues)} epics/stories with due dates")

    due_today, needs_follow_up, at_risk = classify_tickets(
        issues, jira.get_last_comment_date
    )

    # Send due today reminders
    print(f"\n📌 Due today: {len(due_today)} tickets")
    for t in due_today:
        if t["assignee_email"]:
            ticket_url = f"{config['jira']['base_url']}/browse/{t['key']}"
            notifier.send_due_today(
                t["assignee_email"], t["assignee"],
                t["key"], t["summary"], t["due_date"], ticket_url
            )

    # Send follow-up reminders
    print(f"\n⏰ Needs follow-up: {len(needs_follow_up)} tickets")
    for t in needs_follow_up:
        if t["assignee_email"]:
            ticket_url = f"{config['jira']['base_url']}/browse/{t['key']}"
            notifier.send_follow_up(
                t["assignee_email"], t["assignee"],
                t["key"], t["summary"], t["days_overdue"], ticket_url
            )

    # Escalate at-risk tickets
    print(f"\n⚠ At risk: {len(at_risk)} tickets")
    if at_risk:
        print("🤖 Generating AI escalation summary...")
        summary = generate_escalation_summary(at_risk)

        at_risk_formatted = [{
            **t,
            "url": f"{config['jira']['base_url']}/browse/{t['key']}"
        } for t in at_risk]

        notifier.send_escalation(summary, at_risk_formatted)

        for t in at_risk:
            jira.add_label(t["key"], config["jira"]["at_risk_label"])
            jira.add_comment(t["key"], f"🚨 Program Pulse: This item is {t['days_overdue']} days overdue with no update. Escalation sent to leadership.")

        epics_summary = []
        for issue in issues:
            f = issue["fields"]
            from datetime import date
            due = date.fromisoformat(f["duedate"]) if f.get("duedate") else None
            days = (date.today() - due).days if due else 0
            status = "Overdue" if days >= 2 else "At Risk" if days == 1 else "On Track"
            epics_summary.append({
                "key": issue["key"],
                "summary": f["summary"],
                "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                "due_date": f.get("duedate", ""),
                "status": status,
            })
        confluence.update_status_page(epics_summary)
        print("✅ Confluence status page updated")

    print("\n✅ Program Pulse run complete")


def run_demo():
    from demo.demo_runner import run_demo as demo
    demo()


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_live()