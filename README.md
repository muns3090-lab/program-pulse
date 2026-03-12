# 📡 Program Pulse

> An autonomous program health agent that monitors JIRA epics and stories, sends proactive due-date notifications, escalates overdue items to leadership with AI-generated summaries, and keeps your Confluence status page current — all on a daily schedule with zero manual input.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude%20AI-orange.svg)](https://www.anthropic.com)
[![Runs on GitHub Actions](https://img.shields.io/badge/scheduled-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[▶ Live Demo](https://program-pulse.streamlit.app/) |
 **[LinkedIn](https://linkedin.com/in/sss90)**

---

## The Problem

Every Technical Program Manager knows this tax: manually scanning JIRA for overdue items, writing status emails to assignees, drafting leadership escalations, and keeping Confluence status pages from going stale. It's repetitive, it's time-consuming, and it's exactly the kind of work that falls through the cracks when things get busy.

The irony is that this is precisely the work that matters most when a program is at risk — and it's hardest to do consistently when you're already underwater.

---

## What Program Pulse Does

Program Pulse runs every morning as a scheduled agent. It checks your JIRA project, classifies every epic and story by health status, and takes action automatically:

**Day 0 — Item is due today:**
Sends the assignee a direct email reminder with the ticket details and a link to update it.

**Day +1 — Item is overdue, no update:**
Sends the assignee a follow-up asking for a status comment. Flags the item internally.

**Day +2 and beyond — Still no update:**
Generates an AI-written escalation summary using Claude, emails it to your leadership list, adds an `AT-RISK` label to the JIRA ticket, drops a comment on the ticket, and updates your Confluence status page — all in one run.

---

## Demo

> No credentials needed. Run this immediately after cloning.

```bash
python main.py --demo
```

You'll see a full color-coded terminal run showing exactly what the agent would do against a realistic fake program dataset — which emails would send, what the AI escalation summary looks like, and which tickets would get flagged.

```
📡 Program Pulse — Demo Mode
Running against simulated JIRA data. No real credentials needed.

📅 Today's date: 2024-11-18

┌──────────┬──────────────────────────────────────────────┬───────────────┬──────────────────────┐
│ Key      │ Summary                                      │ Assignee      │ Status               │
├──────────┼──────────────────────────────────────────────┼───────────────┼──────────────────────┤
│ PLAT-101 │ Migrate authentication service to OAuth 2.0  │ Alex Chen     │ 📌 Due Today         │
│ PLAT-102 │ Complete API gateway load testing            │ Maria Lopez   │ 📌 Due Today         │
│ PLAT-103 │ ServiceNow-Workday integration UAT sign-off  │ James Park    │ 🟡 Follow-up Needed  │
│ PLAT-104 │ Decommission legacy CMDB → ServiceNow CSDM  │ Sara Williams │ 🔴 At Risk           │
│ INFRA-201│ Zero-trust network segmentation — Phase 2    │ Derek Johnson │ 🔴 At Risk           │
│ PLAT-105 │ Copilot AI integration with ServiceNow       │ Alex Chen     │ 🟢 On Track          │
│ INFRA-202│ Cloud cost optimization — rightsizing        │ Maria Lopez   │ 🟢 On Track          │
└──────────┴──────────────────────────────────────────────┴───────────────┴──────────────────────┘

⚠ AT RISK — ESCALATING (2 tickets)
  → PLAT-104: Decommission legacy CMDB → ServiceNow CSDM (3 days overdue)
  → INFRA-201: Zero-trust network segmentation — Phase 2 (4 days overdue)

🤖 Generating AI escalation summary...

╔══════════════════════════════════════════════════════════════════════════════════╗
║  AI-Generated Leadership Escalation                                              ║
║                                                                                  ║
║  Two critical platform initiatives are currently at risk of missing their        ║
║  delivery commitments. The CMDB migration to ServiceNow CSDM (PLAT-104) has    ║
║  been stalled for 3 days with no status update, with an apparent dependency     ║
║  on the Network team for CI discovery completion that may require leadership     ║
║  intervention. The zero-trust segmentation initiative (INFRA-201) is 4 days    ║
║  overdue and was last flagged as pending a security architecture review from     ║
║  the CISO office...                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════╝

✅ Demo run complete
```

**Or open the live dashboard:** [program-pulse.streamlit.app](https://program-pulse.streamlit.app)

---

## Connecting Your Organization

Setup takes about 5 minutes. You need a JIRA Cloud instance, a Confluence page to write to, and a SendGrid account (free tier covers 100 emails/day).

### 1. Clone and install

```bash
git clone https://github.com/muns3090-lab/program-pulse.git
cd program-pulse

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Mac/Linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the setup wizard

```bash
python setup.py
```

This walks you through entering your credentials, tests each connection live, and writes your `config.yaml` and `.env` automatically.

### 3. Validate everything works

```bash
python validate_connections.py
```

```
✅ JIRA connection: OK (yourcompany.atlassian.net)
✅ Confluence connection: OK (Page: Program Health Dashboard)
✅ SendGrid: OK (test email delivered)
✅ Anthropic API: OK
```

### 4. Run it

```bash
python main.py
```

### 5. Schedule it (optional)

Push to GitHub, add your secrets in repo Settings → Secrets, and the included GitHub Actions workflow handles the rest. Runs automatically every weekday at 8am. No server needed.

---

## Configuration

One file controls everything for your org:

```bash
cp config.yaml.example config.yaml
```

```yaml
jira:
  base_url: "https://yourcompany.atlassian.net"
  email: "you@yourcompany.com"
  project_keys: ["PLAT", "INFRA"]       # which projects to monitor
  at_risk_label: "AT-RISK"

confluence:
  status_page_id: "123456789"           # from your Confluence page URL

notifications:
  email_provider: "sendgrid"            # sendgrid | smtp | ses
  from_address: "pulse@yourcompany.com"
  leader_emails:
    - "vp-engineering@yourcompany.com"
    - "program-director@yourcompany.com"

schedule:
  timezone: "America/Los_Angeles"
  reminder_hour: 8
  escalation_days_overdue: 2            # days before escalating to leaders
```

Sensitive credentials live in `.env` only and are never committed to the repo.

---

## How It Works

```
GitHub Actions (runs daily 8am local time)
         │
         ▼
   main.py agent
         │
         ├─→ JIRA API
         │     └─ Fetch all epics/stories with due dates
         │     └─ Classify: Due Today / Follow-up / At Risk
         │
         ├─→ SendGrid
         │     └─ Assignee reminder (due today)
         │     └─ Assignee follow-up (1 day overdue)
         │     └─ Leadership escalation (2+ days, no update)
         │
         ├─→ Claude API
         │     └─ Generate plain-English escalation summary
         │         (what's at risk, why, what help is needed)
         │
         ├─→ JIRA API
         │     └─ Add AT-RISK label to overdue tickets
         │     └─ Drop comment on ticket with escalation notice
         │
         └─→ Confluence API
               └─ Rewrite status page with current health table
```

---

## Design Decisions

**Why GitHub Actions instead of a server?**
Zero infrastructure cost, zero maintenance, and the workflow file lives in the repo so anyone forking this gets scheduling for free. The `workflow_dispatch` trigger also lets you run it manually anytime from the GitHub UI.

**Why not just use JIRA's built-in notifications?**
JIRA notifications are reactive and noisy. Program Pulse is proactive and selective — it only fires when something needs attention, and the escalation path (assignee → follow-up → leadership) mirrors how a good TPM actually manages a program.

**Why Claude for escalation summaries instead of a template?**
Templates produce robotic emails that people learn to ignore. Claude reads the actual ticket description, assignee context, and delay duration to write something that sounds like a real TPM wrote it — because the reasoning is genuine, not filled-in slots.

**Why a separate demo mode?**
Enterprise data is sensitive. Demo mode means anyone can evaluate the tool, interviewers can see it live, and contributors can test changes without real credentials.

---

## What I'd Build Next

1. **Slack integration** — post the daily health summary to an ops channel instead of (or in addition to) email
2. **Trend dashboard** — health score over time so you can see if a program is improving or degrading week over week
3. **Two-way JIRA updates** — assignees reply to the notification email and it posts back to the ticket automatically
4. **Smart snooze** — assignees reply "blocked — waiting on infra team" and Program Pulse suppresses escalation for 48 hours and flags the blocker instead
5. **Portfolio rollup** — health view across all programs in the org, not just one JIRA project

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11 |
| AI | Anthropic Claude API (claude-sonnet-4-20250514) |
| JIRA + Confluence | Atlassian REST API v3 |
| Email | SendGrid API |
| Scheduling | GitHub Actions (cron) |
| Dashboard | Streamlit |
| Terminal UI | Rich |
| Config | PyYAML + python-dotenv |

---

## Project Structure

```
program-pulse/
├── main.py                      # orchestrator
├── setup.py                     # interactive setup wizard
├── validate_connections.py      # connection health checker
├── dashboard.py                 # streamlit demo dashboard
├── src/
│   ├── jira_client.py           # JIRA API connector
│   ├── confluence_client.py     # Confluence API connector
│   ├── notifier.py              # email sender
│   ├── ai_summary.py            # Claude escalation generator
│   ├── scheduler.py             # due date logic
│   └── config_loader.py        # config + env loader
├── demo/
│   ├── fake_data.py             # realistic fake JIRA dataset
│   └── demo_runner.py           # demo mode orchestrator
├── templates/                   # HTML email templates
├── .github/workflows/
│   └── daily_run.yml            # GitHub Actions scheduler
├── config.yaml.example
├── .env.example
└── requirements.txt
```

---

## About This Project

I'm a Technical Program Manager specializing in ServiceNow and platform modernization. I built Program Pulse because I kept seeing the same problem across every large program I've worked on — the manual overhead of tracking ticket health and escalating proactively is exactly where things fall apart at scale, and it's the kind of work AI agents are well-suited to replace.

This is part of a series of AI tools I'm building at the intersection of enterprise operations and applied AI. If you work in program management, platform engineering, or enterprise tooling and want to collaborate or share feedback, open an issue or connect on [LinkedIn](https://linkedin.com/in/sss90).

---

## License

MIT — use it, fork it, build on it.