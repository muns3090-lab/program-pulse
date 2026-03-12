from datetime import date, timedelta

today = date.today()

FAKE_ISSUES = [
    # Due today — 2 tickets
    {
        "key": "PLAT-101",
        "fields": {
            "summary": "Migrate authentication service to OAuth 2.0",
            "issuetype": {"name": "Epic"},
            "duedate": str(today),
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "Alex Chen", "emailAddress": "alex.chen@demo.com"},
            "labels": [],
            "description": "Full migration of legacy auth system to OAuth 2.0 with SSO support across all internal platforms.",
            "comment": {"comments": []}
        }
    },
    {
        "key": "PLAT-102",
        "fields": {
            "summary": "Complete API gateway load testing",
            "issuetype": {"name": "Story"},
            "duedate": str(today),
            "status": {"name": "In Progress"},
            "priority": {"name": "Medium"},
            "assignee": {"displayName": "Maria Lopez", "emailAddress": "maria.lopez@demo.com"},
            "labels": [],
            "description": "Run load tests against the new API gateway to validate 10k RPS capacity before production cutover.",
            "comment": {"comments": []}
        }
    },
    # Overdue 1 day — needs follow-up
    {
        "key": "PLAT-103",
        "fields": {
            "summary": "ServiceNow-Workday integration UAT sign-off",
            "issuetype": {"name": "Epic"},
            "duedate": str(today - timedelta(days=1)),
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "James Park", "emailAddress": "james.park@demo.com"},
            "labels": [],
            "description": "Obtain UAT sign-off from HR stakeholders on the ServiceNow-Workday integration before go-live.",
            "comment": {"comments": []}
        }
    },
    # Overdue 3 days — AT RISK, no updates
    {
        "key": "PLAT-104",
        "fields": {
            "summary": "Decommission legacy CMDB and migrate to ServiceNow CSDM",
            "issuetype": {"name": "Epic"},
            "duedate": str(today - timedelta(days=3)),
            "status": {"name": "In Progress"},
            "priority": {"name": "Critical"},
            "assignee": {"displayName": "Sara Williams", "emailAddress": "sara.w@demo.com"},
            "labels": [],
            "description": "Full decommission of legacy CMDB system. Migration of 15k CIs to ServiceNow CSDM. Dependency on Network team for CI discovery completion.",
            "comment": {"comments": []}
        }
    },
    {
        "key": "INFRA-201",
        "fields": {
            "summary": "Zero-trust network segmentation — Phase 2",
            "issuetype": {"name": "Epic"},
            "duedate": str(today - timedelta(days=4)),
            "status": {"name": "In Progress"},
            "priority": {"name": "Critical"},
            "assignee": {"displayName": "Derek Johnson", "emailAddress": "derek.j@demo.com"},
            "labels": [],
            "description": "Implement zero-trust network segmentation for production environment. Blocked pending security architecture review from CISO office.",
            "comment": {"comments": []}
        }
    },
    # On track — future due dates
    {
        "key": "PLAT-105",
        "fields": {
            "summary": "Copilot AI integration with ServiceNow incident management",
            "issuetype": {"name": "Epic"},
            "duedate": str(today + timedelta(days=7)),
            "status": {"name": "In Progress"},
            "priority": {"name": "Medium"},
            "assignee": {"displayName": "Alex Chen", "emailAddress": "alex.chen@demo.com"},
            "labels": [],
            "description": "Integrate Microsoft Copilot AI with ServiceNow to auto-suggest incident resolution steps.",
            "comment": {"comments": []}
        }
    },
    {
        "key": "INFRA-202",
        "fields": {
            "summary": "Cloud cost optimization — rightsizing initiative",
            "issuetype": {"name": "Epic"},
            "duedate": str(today + timedelta(days=14)),
            "status": {"name": "To Do"},
            "priority": {"name": "Low"},
            "assignee": {"displayName": "Maria Lopez", "emailAddress": "maria.lopez@demo.com"},
            "labels": [],
            "description": "Analyze and rightsize underutilized cloud resources across AWS and Azure to reduce monthly spend by 20%.",
            "comment": {"comments": []}
        }
    },
]


def get_fake_last_comment(issue_key):
    # Overdue tickets have no recent comments
    return None


FAKE_CONFIG = {
    "jira": {
        "base_url": "https://demo.atlassian.net",
        "email": "demo@company.com",
        "project_keys": ["PLAT", "INFRA"],
        "at_risk_label": "AT-RISK"
    },
    "confluence": {
        "base_url": "https://demo.atlassian.net/wiki",
        "status_page_id": "000000"
    },
    "notifications": {
        "email_provider": "sendgrid",
        "from_address": "pulse@demo.com",
        "leader_emails": ["vp-engineering@demo.com", "program-director@demo.com"]
    },
    "schedule": {
        "timezone": "America/Los_Angeles",
        "reminder_hour": 8,
        "escalation_days_overdue": 2
    }
}