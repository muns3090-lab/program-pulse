from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import date
from demo.fake_data import (
    FAKE_ISSUES, FAKE_CONFIG,
    get_fake_last_comment, get_fake_last_comment_text
)
from src.scheduler import classify_tickets
from src.ai_summary import generate_escalation_summary, generate_overdue_context
from src.escalation_state import was_escalated_recently

console = Console()


def run_demo():
    console.print(Panel.fit(
        "[bold blue]Program Pulse — Demo Mode[/bold blue]\n"
        "[dim]Running against simulated JIRA data. No real credentials needed.[/dim]",
        border_style="blue"
    ))

    console.print(f"\n[bold]📅 Today's date:[/bold] {date.today()}\n")

    due_today, needs_follow_up, at_risk = classify_tickets(
        FAKE_ISSUES, get_fake_last_comment
    )

    # Enrich at-risk tickets with comment text
    for t in at_risk:
        t["last_comment_text"] = get_fake_last_comment_text(t["key"])
    for t in needs_follow_up:
        t["last_comment_text"] = get_fake_last_comment_text(t["key"])

    # Overview table
    table = Table(title="📋 Program Health Overview", box=box.ROUNDED)
    table.add_column("Key", style="cyan", width=12)
    table.add_column("Summary", width=45)
    table.add_column("Assignee", width=18)
    table.add_column("Due Date", width=12)
    table.add_column("Status", width=22)

    today = date.today()
    for issue in FAKE_ISSUES:
        f = issue["fields"]
        due = date.fromisoformat(f["duedate"])
        days = (today - due).days
        if days >= 2:
            status = "[red]⚠ AT RISK[/red]"
        elif days == 1:
            status = "[yellow]⏰ Follow-up Needed[/yellow]"
        elif days == 0:
            status = "[orange3]📌 Due Today[/orange3]"
        else:
            status = "[green]✅ On Track[/green]"

        summary = f["summary"]
        if len(summary) > 43:
            summary = summary[:40] + "..."

        table.add_row(
            issue["key"], summary,
            f["assignee"]["displayName"],
            f["duedate"], status
        )
    console.print(table)

    # Due today
    console.print(f"\n[bold orange3]📌 DUE TODAY ({len(due_today)} tickets)[/bold orange3]")
    for t in due_today:
        console.print(f"  → [cyan]{t['key']}[/cyan] {t['summary']}")
        console.print(f"    [dim]Reminder email would be sent to:[/dim] {t['assignee_email']}")

    # Follow-ups — with AI context preview
    console.print(f"\n[bold yellow]⏰ OVERDUE — FOLLOW-UP NEEDED ({len(needs_follow_up)} tickets)[/bold yellow]")
    for t in needs_follow_up:
        console.print(f"  → [cyan]{t['key']}[/cyan] {t['summary']}")
        console.print(f"    [dim]Follow-up email would be sent to:[/dim] {t['assignee_email']}")
        console.print(f"    [dim]Email includes structured comment request:[/dim]")
        console.print(f"    [dim]  Quick Summary: [1-2 sentences on current status][/dim]")
        console.print(f"    [dim]  Current Blockers: [What is blocking, or None][/dim]")

    # At risk — with 7-day cooldown check
    console.print(f"\n[bold red]⚠  AT RISK — ESCALATION CHECK ({len(at_risk)} tickets)[/bold red]")

    tickets_to_escalate = []
    for t in at_risk:
        recently = was_escalated_recently(t["key"])
        if recently:
            console.print(f"  ⏭ [dim]{t['key']} — skipping, escalation sent within last 7 days[/dim]")
        else:
            tickets_to_escalate.append(t)
            console.print(f"  → [red]{t['key']}[/red] {t['summary']} ({t['days_overdue']}d overdue)")
            console.print(f"    [dim]Would add AT-RISK label in JIRA[/dim]")
            if t.get("last_comment_text"):
                console.print(f"    [dim]Last comment: \"{t['last_comment_text'][:80]}...\"[/dim]")

    if tickets_to_escalate:
        console.print("\n[bold]🤖 Generating AI escalation summary from ticket context + latest comments...[/bold]")
        summary = generate_escalation_summary(tickets_to_escalate)
        console.print(Panel(
            summary,
            title="[bold red]Leadership Escalation Email — AI Generated[/bold red]",
            subtitle="[dim]Sections: Quick Summary | Current Blockers | What Is Needed | Business Value If Not Done[/dim]",
            border_style="red",
            padding=(1, 2)
        ))
        console.print(f"  [dim]Would send to:[/dim] {FAKE_CONFIG['notifications']['leader_emails']}")
        console.print(f"  [dim]Next escalation for these tickets:[/dim] 7 days from today")
    elif at_risk:
        console.print("\n  [green]All at-risk tickets were escalated recently. No emails sent today.[/green]")

    console.print(Panel.fit(
        "[bold green]✅ Demo run complete[/bold green]\n"
        "[dim]In live mode, all actions above execute against real JIRA, Confluence, and email.[/dim]",
        border_style="green"
    ))

    return {
        "due_today": due_today,
        "needs_follow_up": needs_follow_up,
        "at_risk": at_risk,
        "tickets_escalated": tickets_to_escalate,
        "config": FAKE_CONFIG
    }