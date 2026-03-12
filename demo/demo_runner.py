from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import date
from demo.fake_data import FAKE_ISSUES, FAKE_CONFIG, get_fake_last_comment
from src.scheduler import classify_tickets
from src.ai_summary import generate_escalation_summary

console = Console()


def run_demo():
    console.print(Panel.fit(
        "[bold blue]Program Pulse — Demo Mode[/bold blue]\n"
        "[dim]Running against simulated JIRA data. No real credentials needed.[/dim]",
        border_style="blue"
    ))

    console.print(f"\n[bold]📅 Today's date:[/bold] {date.today()}\n")

    # Classify tickets
    due_today, needs_follow_up, at_risk = classify_tickets(
        FAKE_ISSUES, get_fake_last_comment
    )

    # Show all epics table
    table = Table(title="📋 All Epics & Stories", box=box.ROUNDED)
    table.add_column("Key", style="cyan")
    table.add_column("Summary")
    table.add_column("Assignee")
    table.add_column("Due Date")
    table.add_column("Status")

    today = date.today()
    for issue in FAKE_ISSUES:
        f = issue["fields"]
        due = date.fromisoformat(f["duedate"])
        days = (today - due).days
        if days > 1:
            status = "[red]⚠ AT RISK[/red]"
        elif days == 1:
            status = "[yellow]⏰ Follow-up Needed[/yellow]"
        elif days == 0:
            status = "[orange3]📌 Due Today[/orange3]"
        else:
            status = "[green]✅ On Track[/green]"

        table.add_row(
            issue["key"],
            f["summary"][:50] + "..." if len(f["summary"]) > 50 else f["summary"],
            f["assignee"]["displayName"],
            f["duedate"],
            status
        )
    console.print(table)

    # Due today
    console.print(f"\n[bold orange3]📌 DUE TODAY ({len(due_today)} tickets)[/bold orange3]")
    for t in due_today:
        console.print(f"  → [cyan]{t['key']}[/cyan] {t['summary']}")
        console.print(f"    [dim]Would send reminder email to:[/dim] {t['assignee_email']}")

    # Follow-up needed
    console.print(f"\n[bold yellow]⏰ FOLLOW-UP NEEDED ({len(needs_follow_up)} tickets)[/bold yellow]")
    for t in needs_follow_up:
        console.print(f"  → [cyan]{t['key']}[/cyan] {t['summary']}")
        console.print(f"    [dim]Would send follow-up email to:[/dim] {t['assignee_email']}")

    # At risk
    console.print(f"\n[bold red]⚠ AT RISK — ESCALATING ({len(at_risk)} tickets)[/bold red]")
    for t in at_risk:
        console.print(f"  → [cyan]{t['key']}[/cyan] {t['summary']} ({t['days_overdue']} days overdue)")
        console.print(f"    [dim]Would add AT-RISK label in JIRA[/dim]")

    if at_risk:
        console.print("\n[bold]🤖 Generating AI escalation summary...[/bold]")
        summary = generate_escalation_summary(at_risk)
        console.print(Panel(
            summary,
            title="[bold red]AI-Generated Leadership Escalation[/bold red]",
            border_style="red"
        ))
        console.print(f"  [dim]Would send escalation email to:[/dim] {FAKE_CONFIG['notifications']['leader_emails']}")
        console.print(f"  [dim]Would update Confluence status page ID:[/dim] {FAKE_CONFIG['confluence']['status_page_id']}")

    console.print(Panel.fit(
        "[bold green]✅ Demo run complete[/bold green]\n"
        "[dim]In live mode, all actions above would execute against real JIRA, Confluence, and email.[/dim]",
        border_style="green"
    ))

    return {
        "due_today": due_today,
        "needs_follow_up": needs_follow_up,
        "at_risk": at_risk,
        "config": FAKE_CONFIG
    }