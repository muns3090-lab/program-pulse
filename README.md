# 📡 Program Pulse

> An autonomous program health agent that monitors JIRA epics and stories, sends proactive due-date notifications, escalates overdue items to leadership with AI-generated summaries, and keeps your Confluence status page current — all on a daily schedule with zero manual input.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude%20AI-orange.svg)](https://www.anthropic.com)
[![Runs on GitHub Actions](https://img.shields.io/badge/scheduled-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[▶ Live Demo](https://program-pulse.streamlit.app)** | **[LinkedIn](https://linkedin.com/in/sss90)**

---

## The Problem

Every Technical Program Manager knows this tax: manually scanning JIRA for overdue items, chasing assignees for updates, drafting leadership escalations, and keeping Confluence status pages from going stale.

It's repetitive, time-consuming, and — ironically — hardest to do consistently when a program is already at risk and you need it most.

---

## What It Does

Program Pulse runs every morning as a scheduled agent. It checks your JIRA projects, classifies every epic and story by health status, and takes the right action automatically based on how overdue each item is.

| Scenario | What Program Pulse Does |
|---|---|
| Item due today | Sends assignee a direct reminder email with ticket details and JIRA link |
| 1 day overdue, no update | Sends assignee a follow-up asking for a structured status comment |
| 2+ days overdue, still no update | Generates AI escalation summary → emails leadership → labels ticket AT-RISK → updates Confluence |
| Already escalated within 7 days | Skips — no repeat emails to leadership until the cooldown window passes |

### The leadership escalation email is structured, not generic

Rather than a boilerplate "ticket is overdue" notice, Claude reads the actual ticket context and latest JIRA comments to generate a structured summary with four sections every leader wants:

- **Quick Summary** — what's at risk and for how long
- **Current Blockers** — specific reasons for the delay based on ticket context
- **What Is Needed** — concrete, actionable asks of leadership
- **Business Value If Not Done** — delivery, compliance, or operational risk

### The assignee follow-up prompts a standard update format

Overdue assignees receive an email that asks them to post a comment in JIRA using a consistent format:

```
Quick Summary: [1-2 sentences on current status]
Current Blockers: [What is blocking, or "None"]
```

This keeps program data structured and makes the AI escalation summaries more accurate.

---

## Live Demo

No credentials needed. Run this immediately after cloning:

```bash
python main.py --demo
```

You'll see a full color-coded terminal run against a realistic fake program dataset — which emails would fire, the AI escalation summary, which tickets get flagged, and the 7-day cooldown logic in action.

Or open the **[live Streamlit dashboard](https://program-pulse.streamlit.app)** to see the demo in your browser with no setup.

```
📡 Program Pulse — Demo Mode

📅 Today's date: 2024-11-18

  Key        Summary                                      Assignee       Due Date    Status
  PLAT-101   Migrate auth service to OAuth 2.0            Alex Chen      2024-11-18  📌 Due Today
  PLAT-102   Complete API gateway load testing            Maria Lopez    2024-11-18  📌 Due Today
  PLAT-103   ServiceNow-Workday integration UAT sign-off  James Park     2024-11-17  🟡 Follow-up Needed
  PLAT-104   Decommission legacy CMDB → ServiceNow CSDM  Sara Williams  2024-11-15  🔴 AT RISK
  INFRA-201  Zero-trust network segmentation — Phase 2   Derek Johnson  2024-11-14  🔴 AT RISK
  PLAT-105   Copilot AI integration with ServiceNow       Alex Chen      2024-11-25  🟢 On Track
  INFRA-202  Cloud cost optimization — rightsizing        Maria Lopez    2024-12-02  🟢 On Track

⚠  AT RISK — ESCALATING (2 tickets)

🤖 Generating AI escalation summary from ticket context + latest comments...

  ╔══════════════════════════════════════════════════════════════════╗
  ║  Leadership Escalation — AI Generated                           ║
  ║                                                                  ║
  ║  Quick Summary                                                   ║
  ║  Two critical platform initiatives are 3–4 days overdue with    ║
  ║  no assignee updates. Both carry hard dependencies on external  ║
  ║  teams that appear to be unresolved.                            ║
  ║                                                                  ║
  ║  Current Blockers                                               ║
  ║  • PLAT-104: Network team backlogged on CI discovery scan       ║
  ║  • INFRA-201: CISO security architecture review not scheduled   ║
  ║                                                                  ║
  ║  What Is Needed                                                  ║
  ║  • Leadership to unblock Network team prioritization            ║
  ║  • Someone to escalate CISO review scheduling for INFRA-201    ║
  ║                                                                  ║
  ║  Business Value If Not Done                                      ║
  ║  Delay to CMDB migration risks audit compliance gaps in Q4.     ║
  ║  Zero-trust delay extends production exposure window.           ║
  ╚══════════════════════════════════════════════════════════════════╝

  Next escalation for these tickets: 7 days from today
```

---

## Connecting Your Organization

Setup takes about 5 minutes. You need a JIRA Cloud instance, a Confluence page to write status updates to, a [SendGrid account](https://sendgrid.com) (free tier: 100 emails/day), and an [Anthropic API key](https://console.anthropic.com).

### Step 1 — Clone and install

```powershell
# Windows PowerShell
git clone https://github.com/muns3090-lab/program-pulse.git
cd program-pulse
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Mac / Linux
git clone https://github.com/muns3090-lab/program-pulse.git
cd program-pulse
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Step 2 — Run the setup wizard

```bash
python setup.py
```

The wizard prompts for each credential, tests the connection live, and writes `config.yaml` and `.env` automatically.

### Step 3 — Validate everything

```bash
python validate_connections.py
```

```
✅ JIRA connection OK  →  yourcompany.atlassian.net
✅ Confluence connection OK  →  Program Health Dashboard
✅ SendGrid OK  →  test email delivered
✅ Anthropic API OK
```

### Step 4 — Run

```bash
python main.py
```

### Step 5 — Schedule it (optional but recommended)

Push to GitHub, add your credentials under repo Settings → Secrets → Actions, and the included GitHub Actions workflow runs the agent every weekday at 8am automatically. No server or cron job needed.

---

## Configuration Reference

```yaml
# config.yaml — copy from config.yaml.example

jira:
  base_url: "https://yourcompany.atlassian.net"
  email: "you@yourcompany.com"
  project_keys: ["PLAT", "INFRA"]       # which JIRA projects to monitor
  at_risk_label: "AT-RISK"

confluence:
  status_page_id: "123456789"           # from your Confluence page URL

notifications:
  email_provider: "sendgrid"
  from_address: "pulse@yourcompany.com"
  leader_emails:
    - "vp-engineering@yourcompany.com"
    - "program-director@yourcompany.com"

schedule:
  timezone: "America/Los_Angeles"
  reminder_hour: 8
  escalation_days_overdue: 2            # days before escalating to leaders
  escalation_cooldown_days: 7           # days before re-escalating same ticket
```

Sensitive keys live in `.env` only and are never committed to the repo.

---

## How the Escalation Cooldown Works

Program Pulse tracks every escalation in a local `state.json` file. When an at-risk ticket is escalated, the date is recorded. On subsequent runs, the agent checks whether 7 days have passed before sending another leadership email.

- Leadership gets notified when something first goes at risk
- They don't get repeat emails every day for the same item
- After 7 days, if still unresolved, a fresh escalation fires with updated context pulled from any new comments
- When a ticket is resolved or closed, its entry is cleared automatically

The `state.json` file is preserved between GitHub Actions runs via the Actions cache, so the cooldown works correctly across daily scheduled runs.

---

## Architecture

```
GitHub Actions (runs daily at 8am)
        │
        ▼
  main.py orchestrator
        │
        ├─→ src/jira_client.py
        │       Fetch all epics + stories with due dates (JQL)
        │       Read last comment date and text per ticket
        │       Add AT-RISK label + bot comment on escalated tickets
        │
        ├─→ src/scheduler.py
        │       Classify: Due Today / Follow-up Needed / At Risk
        │
        ├─→ src/escalation_state.py
        │       Check 7-day cooldown per ticket (state.json)
        │       Mark tickets as escalated after sending
        │
        ├─→ src/ai_summary.py  (Claude API)
        │       generate_escalation_summary() → 4-section leadership email
        │       generate_overdue_context()    → assignee nudge context blurb
        │
        ├─→ src/notifier.py  (SendGrid)
        │       send_due_today()   → assignee reminder on due date
        │       send_follow_up()   → assignee follow-up with comment format
        │       send_escalation()  → structured leadership alert
        │
        └─→ src/confluence_client.py
                Rewrite status page with current health table
```

---

## Design Decisions

**Why GitHub Actions instead of a server?**
Zero infrastructure, zero maintenance, and the workflow file lives in the repo so anyone forking this gets scheduling automatically. The `workflow_dispatch` trigger also lets you run manually from the GitHub UI anytime — useful for mid-day checks or post-deployment.

**Why not just use JIRA's built-in notifications?**
JIRA notifications are reactive and noisy — every comment and status change fires an alert. Program Pulse is proactive and selective. It only fires when something needs attention, and the escalation path mirrors how an experienced TPM actually manages a program: assignee first, then leadership only if there's no response.

**Why Claude for escalation summaries instead of templates?**
Templates produce robotic emails that leaders learn to ignore. Claude reads the actual ticket descriptions and latest JIRA comments to surface real blockers and specific asks. The structured format — Quick Summary, Current Blockers, What Is Needed, Business Value — ensures every escalation email is immediately actionable for a VP or director.

**Why a 7-day escalation cooldown?**
Daily escalation emails for the same unresolved ticket train leadership to tune them out. A weekly cadence matches how most program reviews work, and the re-escalation carries fresh context from whatever comments have been added in the interim.

**Why prompt assignees to use a specific comment format?**
Unstructured comments like "still working on it" don't help anyone. Asking for Quick Summary + Current Blockers produces structured data that feeds back into the AI escalation summary, making it more accurate over time.

---

## What I'd Build Next

1. **Slack integration** — post the daily health summary to an ops channel; assignees can react with ✅ to acknowledge without leaving Slack
2. **Smart snooze** — assignees reply "blocked — waiting on infra team ETA Friday" and the agent suppresses escalation until that date, flagging the specific blocker instead
3. **Health trend tracking** — program health score over time so you can see whether a program is improving or degrading week over week
4. **Two-way email-to-JIRA bridge** — assignees reply to the notification email and Program Pulse posts it back as a JIRA comment automatically
5. **Portfolio rollup** — cross-program health view for a Director or VP overseeing multiple programs simultaneously

---

## Project Structure

```
program-pulse/
├── main.py                       # orchestrator — run with --demo or live
├── setup.py                      # interactive setup wizard
├── validate_connections.py       # connection health checker
├── dashboard.py                  # streamlit demo dashboard
│
├── src/
│   ├── jira_client.py            # JIRA REST API v3 connector
│   ├── confluence_client.py      # Confluence REST API connector
│   ├── notifier.py               # SendGrid email sender (3 email types)
│   ├── ai_summary.py             # Claude escalation + context generator
│   ├── scheduler.py              # due date classification logic
│   ├── escalation_state.py       # 7-day cooldown tracker (state.json)
│   └── config_loader.py          # config.yaml + .env loader
│
├── demo/
│   ├── fake_data.py              # realistic fake JIRA dataset (7 tickets)
│   └── demo_runner.py            # demo mode orchestrator with Rich UI
│
├── templates/                    # HTML email templates
│
├── .github/workflows/
│   └── daily_run.yml             # GitHub Actions cron scheduler
│
├── config.yaml.example           # copy this → config.yaml and fill in
├── .env.example                  # copy this → .env and add API keys
└── requirements.txt
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11 |
| AI | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| JIRA + Confluence | Atlassian REST API v3 |
| Email | SendGrid API |
| Scheduling | GitHub Actions (cron) |
| Dashboard | Streamlit |
| Terminal UI | Rich |
| Config | PyYAML + python-dotenv |
| Cost to run | < $1/month |

---

## About This Project

I'm a Technical Program Manager specializing in ServiceNow and platform modernization. I built Program Pulse because I kept encountering the same problem across every large program — the manual overhead of proactive ticket health management is exactly where programs fall apart at scale, and it's precisely the kind of structured, repeatable work that AI agents handle well.

This is part of a series of AI tools I'm building at the intersection of enterprise operations and applied AI. If you work in program management, platform engineering, or enterprise tooling and want to collaborate or share feedback, open an issue or connect on [LinkedIn](https://linkedin.com/in/sss90).

---

## License

MIT — use it, fork it, build on it.