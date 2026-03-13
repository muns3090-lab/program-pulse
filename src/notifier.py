"""
Email notifications for Program Pulse.

Three email types:
  1. due_today    — sent to assignee on the due date
  2. follow_up    — sent to assignee when overdue, asks for structured comment
  3. escalation   — sent to leadership with AI-structured summary (max once per 7 days per ticket)
"""

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

    # ------------------------------------------------------------------
    # 1. Due today reminder
    # ------------------------------------------------------------------

    def send_due_today(self, to_email, assignee_name, ticket_key,
                       ticket_summary, due_date, ticket_url):
        subject = f"[Program Pulse] Due Today: {ticket_key} — {ticket_summary}"
        body = f"""
        <p>Hi {assignee_name},</p>

        <p>This is your daily reminder that the following item is <strong>due today</strong>:</p>

        <table style="border-collapse:collapse;width:100%;max-width:600px">
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc;width:140px">
                    <strong>Ticket</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0">
                    <a href="{ticket_url}">{ticket_key}</a>
                </td>
            </tr>
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc">
                    <strong>Summary</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0">{ticket_summary}</td>
            </tr>
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc">
                    <strong>Due Date</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0">{due_date}</td>
            </tr>
        </table>

        <p>Please update the ticket status in JIRA today.</p>

        <p style="color:#888;font-size:12px;border-top:1px solid #e2e8f0;padding-top:12px;margin-top:20px">
            Sent by Program Pulse — automated program health agent
        </p>
        """
        self._send(to_email, subject, body)

    # ------------------------------------------------------------------
    # 2. Overdue follow-up — asks assignee for structured comment
    # ------------------------------------------------------------------

    def send_follow_up(self, to_email, assignee_name, ticket_key,
                       ticket_summary, days_overdue, ticket_url,
                       ai_context: str = ""):
        subject = f"[Program Pulse] Update Needed: {ticket_key} is {days_overdue} day(s) overdue"

        ai_block = ""
        if ai_context:
            ai_block = f"""
            <div style="background:#EFF6FF;padding:14px;border-left:4px solid #3B82F6;
                        border-radius:4px;margin:16px 0">
                <strong>Context reminder:</strong><br>
                {ai_context}
            </div>
            """

        body = f"""
        <p>Hi {assignee_name},</p>

        <p>The following item is <strong>{days_overdue} day(s) overdue</strong> and has no status
        update in JIRA:</p>

        <table style="border-collapse:collapse;width:100%;max-width:600px">
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc;width:140px">
                    <strong>Ticket</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0">
                    <a href="{ticket_url}">{ticket_key}</a>
                </td>
            </tr>
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc">
                    <strong>Summary</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0">{ticket_summary}</td>
            </tr>
            <tr>
                <td style="padding:10px;border:1px solid #e2e8f0;background:#f8fafc">
                    <strong>Days Overdue</strong>
                </td>
                <td style="padding:10px;border:1px solid #e2e8f0;color:#DC2626">
                    <strong>{days_overdue} day(s)</strong>
                </td>
            </tr>
        </table>

        {ai_block}

        <p>Please <a href="{ticket_url}">add a comment in JIRA</a> today using this format:</p>

        <div style="background:#F0FDF4;padding:16px;border-left:4px solid #22C55E;
                    border-radius:4px;margin:16px 0;font-family:monospace;font-size:14px">
            <strong>Quick Summary:</strong> [1-2 sentences on current status]<br><br>
            <strong>Current Blockers:</strong> [What is blocking progress, or "None"]
        </div>

        <p>This update helps the program team understand where things stand and whether
        you need any help or unblocking from leadership.</p>

        <p>If you are blocked, reply to this email and we will escalate immediately.</p>

        <p style="color:#888;font-size:12px;border-top:1px solid #e2e8f0;
                  padding-top:12px;margin-top:20px">
            Sent by Program Pulse — automated program health agent
        </p>
        """
        self._send(to_email, subject, body)

    # ------------------------------------------------------------------
    # 3. Leadership escalation — structured AI summary
    # ------------------------------------------------------------------

    def send_escalation(self, ai_summary: str, at_risk_tickets: list[dict]):
        ticket_count = len(at_risk_tickets)
        subject = (
            f"[Program Pulse] ⚠️ Program Health Alert — "
            f"{ticket_count} item{'s' if ticket_count > 1 else ''} At Risk"
        )

        tickets_html = "".join([
            f"""
            <tr>
                <td style="padding:8px;border:1px solid #e2e8f0">
                    <a href="{t['url']}">{t['key']}</a>
                </td>
                <td style="padding:8px;border:1px solid #e2e8f0">{t['summary']}</td>
                <td style="padding:8px;border:1px solid #e2e8f0">{t['assignee']}</td>
                <td style="padding:8px;border:1px solid #e2e8f0;color:#DC2626">
                    {t['days_overdue']}d overdue
                </td>
            </tr>
            """
            for t in at_risk_tickets
        ])

        # Convert AI markdown-style bold to HTML for email rendering
        formatted_summary = (ai_summary
            .replace("**Quick Summary**", "<h3 style='color:#1E40AF;margin-top:16px'>📋 Quick Summary</h3>")
            .replace("**Current Blockers**", "<h3 style='color:#DC2626;margin-top:16px'>🚧 Current Blockers</h3>")
            .replace("**What Is Needed**", "<h3 style='color:#D97706;margin-top:16px'>🙋 What Is Needed</h3>")
            .replace("**Business Value If Not Done**", "<h3 style='color:#7C3AED;margin-top:16px'>💼 Business Value If Not Done</h3>")
            .replace("\n- ", "<br>• ")
            .replace("\n", "<br>")
        )

        body = f"""
        <p>Hi team,</p>

        <p>Program Pulse has flagged the following items as
        <strong style="color:#DC2626">At Risk</strong>.
        These tickets are overdue with no status updates from assignees.</p>

        <table style="border-collapse:collapse;width:100%;max-width:700px">
            <thead>
                <tr style="background:#F1F5F9">
                    <th style="padding:10px;border:1px solid #e2e8f0;text-align:left">Ticket</th>
                    <th style="padding:10px;border:1px solid #e2e8f0;text-align:left">Summary</th>
                    <th style="padding:10px;border:1px solid #e2e8f0;text-align:left">Assignee</th>
                    <th style="padding:10px;border:1px solid #e2e8f0;text-align:left">Status</th>
                </tr>
            </thead>
            <tbody>{tickets_html}</tbody>
        </table>

        <div style="background:#FFFBEB;padding:20px;border:1px solid #FDE68A;
                    border-radius:6px;margin-top:24px">
            <h2 style="margin-top:0;color:#92400E">AI-Generated Program Status</h2>
            <p style="color:#78350F;font-size:12px;margin-bottom:16px">
                Generated by Claude based on ticket descriptions and latest JIRA comments
            </p>
            {formatted_summary}
        </div>

        <p style="margin-top:20px">These tickets have been labeled
        <strong>AT-RISK</strong> in JIRA and the Confluence status page has been updated.</p>

        <p style="color:#888;font-size:12px;border-top:1px solid #e2e8f0;
                  padding-top:12px;margin-top:20px">
            Sent by Program Pulse — automated program health agent<br>
            Next escalation reminder for these tickets: 7 days from today
        </p>
        """

        for leader in self.leader_emails:
            self._send(leader, subject, body)

    # ------------------------------------------------------------------
    # Internal send
    # ------------------------------------------------------------------

    def _send(self, to_email: str, subject: str, html_body: str):
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_body
        )
        try:
            self.sg.send(message)
            print(f"  ✅ Email sent → {to_email}")
        except Exception as e:
            print(f"  ❌ Failed to send → {to_email}: {e}")