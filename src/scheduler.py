from datetime import date, timedelta


def classify_tickets(issues, get_last_comment_fn):
    today = date.today()
    due_today = []
    needs_follow_up = []
    at_risk = []

    for issue in issues:
        fields = issue["fields"]
        due_str = fields.get("duedate")
        if not due_str:
            continue

        due_date = date.fromisoformat(due_str)
        days_overdue = (today - due_date).days

        assignee = fields.get("assignee") or {}
        ticket = {
            "key": issue["key"],
            "summary": fields.get("summary", ""),
            "assignee": assignee.get("displayName", "Unassigned"),
            "assignee_email": (assignee.get("emailAddress", "")),
            "due_date": due_str,
            "days_overdue": days_overdue,
            "status": fields.get("status", {}).get("name", ""),
            "description": str(fields.get("description") or "")[:300],
            "labels": fields.get("labels", []),
        }

        if days_overdue == 0:
            due_today.append(ticket)
        elif days_overdue == 1:
            last_comment = get_last_comment_fn(issue["key"])
            ticket["last_comment"] = str(last_comment)
            if not last_comment or last_comment < due_date:
                needs_follow_up.append(ticket)
        elif days_overdue >= 2:
            last_comment = get_last_comment_fn(issue["key"])
            ticket["last_comment"] = str(last_comment)
            if not last_comment or last_comment < due_date:
                at_risk.append(ticket)

    return due_today, needs_follow_up, at_risk