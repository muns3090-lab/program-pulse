"""
Tracks when escalation emails were last sent per ticket.
Prevents leadership from receiving repeat emails within the cooldown window.
State is stored in state.json at the project root.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / "state.json"
DEFAULT_COOLDOWN_DAYS = 7


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def was_escalated_recently(ticket_key: str, cooldown_days: int = DEFAULT_COOLDOWN_DAYS) -> bool:
    """Returns True if an escalation email was sent for this ticket within cooldown window."""
    state = load_state()
    last_sent_str = state.get(ticket_key, {}).get("escalation_sent")
    if not last_sent_str:
        return False
    last_sent = date.fromisoformat(last_sent_str)
    days_since = (date.today() - last_sent).days
    return days_since < cooldown_days


def mark_escalated(ticket_key: str):
    """Record that an escalation email was sent today for this ticket."""
    state = load_state()
    if ticket_key not in state:
        state[ticket_key] = {}
    state[ticket_key]["escalation_sent"] = str(date.today())
    save_state(state)


def get_days_since_escalation(ticket_key: str) -> int | None:
    """Returns how many days since last escalation, or None if never escalated."""
    state = load_state()
    last_sent_str = state.get(ticket_key, {}).get("escalation_sent")
    if not last_sent_str:
        return None
    return (date.today() - date.fromisoformat(last_sent_str)).days


def clear_resolved_tickets(resolved_keys: list[str]):
    """Remove state entries for tickets that are now resolved/closed."""
    state = load_state()
    for key in resolved_keys:
        state.pop(key, None)
    save_state(state)