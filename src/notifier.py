import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()


class Notifier:
    def __init__(self, config):
        self.provider = config["notifications"].get("email_provider", "sendgrid")
        self.from_email = config["notifications"]["from_address"]
        self.leader_emails = config["notifications"]["leader_emails"]
        self.sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))

    def send_due_today(self, to_email, assignee_name, ticket_key, ticket_summary, due_date, ticket_url):
        subject = f"[Program Pulse] Due Today: {ticket_key} — {ticket_summary}"
        body = f"""
        <p>Hi {assignee_name},</p>
        <p>This is your daily reminder that the following item is <strong>due today</strong>:</p>
        <table style="border-collapse:collapse;width:100%">
            <tr><td style="padding:8px;border:1px solid #ddd"><strong>Ticket</strong></td>
                <td style="padding:8px;border:1px solid #ddd"><a href="{ticket_url}">{ticket_key}</a></td></tr>
            <tr><td style="padding:8px;border:1px solid #ddd"><strong>Summary</strong></td>
                <td style="padding:8px;border:1px solid #ddd">{ticket_summary}</td></tr>
            <tr><td style="padding:8px;border:1px solid #ddd"><strong>Due Date</strong></td>
                <td style="padding:8px;border:1px solid #ddd">{due_date}</td></tr>
        </table>
        <p>Please update the ticket status in JIRA today.</p>
        <p style="color:#888;font-size:12px">Sent by Program Pulse — automated program health agent</p>
        """
        self._send(to_email, subject, body)

    def send_follow_up(self, to_email, assignee_name, ticket_key, ticket_summary, days_overdue, ticket_url):
        subject = f"[Program Pulse] Update Needed: {ticket_key} — {days_overdue} day(s) overdue"
        body = f"""
        <p>Hi {assignee_name},</p>
        <p>The following item is now <strong>{days_overdue} day(s) overdue</strong> with no status update:</p>
        <table style="border-collapse:collapse;width:100%">
            <tr><td style="padding:8px;border:1px solid #ddd"><strong>Ticket</strong></td>
                <td style="padding:8px;border:1px solid #ddd"><a href="{ticket_url}">{ticket_key}</a></td></tr>
            <tr><td style="padding:8px;border:1px solid #ddd"><strong>Summary</strong></td>
                <td style="padding:8px;border:1px solid #ddd">{ticket_summary}</td></tr>
        </table>
        <p>Please add a comment in JIRA with a status update today. If you need help or are blocked, reply to this email.</p>
        <p style="color:#888;font-size:12px">Sent by Program Pulse — automated program health agent</p>
        """
        self._send(to_email, subject, body)

    def send_escalation(self, ai_summary, at_risk_tickets):
        subject = f"[Program Pulse] ⚠️ Program Health Alert — {len(at_risk_tickets)} item(s) At Risk"
        tickets_html = "".join([
            f"<li><a href='{t['url']}'>{t['key']}</a> — {t['summary']} (Assignee: {t['assignee']}, {t['days_overdue']} days overdue)</li>"
            for t in at_risk_tickets
        ])
        body = f"""
        <p>Hi team,</p>
        <p>Program Pulse has flagged the following items as <strong style="color:#FF5630">At Risk</strong>:</p>
        <ul>{tickets_html}</ul>
        <h3>AI-Generated Status Summary</h3>
        <div style="background:#FFF8E1;padding:16px;border-left:4px solid #FF991F;">
            {ai_summary}
        </div>
        <p>These tickets have been labeled AT-RISK in JIRA and the Confluence status page has been updated.</p>
        <p style="color:#888;font-size:12px">Sent by Program Pulse — automated program health agent</p>
        """
        for leader in self.leader_emails:
            self._send(leader, subject, body)

    def _send(self, to_email, subject, html_body):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )
        try:
            self.sg.send(message)
            print(f"  ✅ Email sent to {to_email}")
        except Exception as e:
            print(f"  ❌ Failed to send to {to_email}: {e}")