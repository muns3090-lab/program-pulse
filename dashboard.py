import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Program Pulse",
    page_icon="📡",
    layout="wide"
)

# Header
st.markdown("# 📡 Program Pulse")
st.markdown("*Autonomous program health agent — monitors JIRA, sends smart notifications, escalates with AI*")
st.divider()

# Mode selector
mode = st.sidebar.radio("Mode", ["🎮 Demo Mode", "🔴 Live Mode"])
st.sidebar.divider()
st.sidebar.markdown("**Program Pulse** monitors your JIRA epics and stories, sends proactive due-date reminders, and escalates overdue items to leadership with AI-generated summaries.")
st.sidebar.divider()
st.sidebar.markdown("[GitHub](https://github.com/muns3090-lab/program-pulse) | [LinkedIn](https://linkedin.com/in/sss90)")

if "🎮 Demo" in mode:
    from demo.fake_data import FAKE_ISSUES, FAKE_CONFIG
    from src.scheduler import classify_tickets
    from src.ai_summary import generate_escalation_summary

    issues = FAKE_ISSUES
    config = FAKE_CONFIG

    def get_fake_last_comment(key):
        return None

    today = date.today()
    due_today, needs_follow_up, at_risk = classify_tickets(issues, get_fake_last_comment)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Epics/Stories", len(issues))
    col2.metric("Due Today", len(due_today), delta="reminders sent" if due_today else None)
    col3.metric("Needs Follow-up", len(needs_follow_up), delta="⏰" if needs_follow_up else None, delta_color="off")
    col4.metric("At Risk 🔴", len(at_risk), delta="escalated" if at_risk else None, delta_color="inverse")

    st.divider()

    # Epic status cards
    st.subheader("📋 Program Health Overview")

    rows = []
    for issue in issues:
        f = issue["fields"]
        due = date.fromisoformat(f["duedate"])
        days = (today - due).days
        if days >= 2:
            status = "🔴 At Risk"
        elif days == 1:
            status = "🟡 Follow-up Needed"
        elif days == 0:
            status = "🟠 Due Today"
        else:
            status = "🟢 On Track"

        rows.append({
            "Key": issue["key"],
            "Summary": f["summary"],
            "Assignee": f["assignee"]["displayName"],
            "Due Date": f["duedate"],
            "Days Overdue": max(days, 0),
            "Status": status
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Notifications log
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📬 Today's Notification Log")
        if due_today:
            for t in due_today:
                st.success(f"✉️ **Reminder sent** → {t['assignee']} ({t['assignee_email']})\n\n{t['key']}: {t['summary']}")
        if needs_follow_up:
            for t in needs_follow_up:
                st.warning(f"⏰ **Follow-up sent** → {t['assignee']} ({t['assignee_email']})\n\n{t['key']}: {t['summary']} ({t['days_overdue']}d overdue)")
        if at_risk:
            for t in at_risk:
                st.error(f"🚨 **Escalated** → Leadership\n\n{t['key']}: {t['summary']} ({t['days_overdue']}d overdue)")

    with col_right:
        st.subheader("🤖 AI Escalation Summary")
        if at_risk:
            if st.button("Generate AI Summary", type="primary"):
                with st.spinner("Claude is analyzing overdue tickets..."):
                    summary = generate_escalation_summary(at_risk)
                    st.session_state["ai_summary"] = summary

            if "ai_summary" in st.session_state:
                st.markdown(f"""
                <div style="background:#FFF8E1;padding:16px;border-left:4px solid #FF991F;border-radius:4px;">
                {st.session_state['ai_summary']}
                </div>
                """, unsafe_allow_html=True)
                st.caption("This summary was sent to: " + ", ".join(config["notifications"]["leader_emails"]))
        else:
            st.info("No at-risk items today. No escalation needed. ✅")

    st.divider()

    # Confluence preview
    st.subheader("📄 Confluence Status Page Preview")
    st.caption("This is what Program Pulse would write to your Confluence page after each run")
    confluence_df = df[["Key", "Summary", "Assignee", "Due Date", "Status"]].copy()
    st.table(confluence_df)

else:
    st.info("Live mode requires a configured `config.yaml` and `.env` file. See the README for setup instructions.")
    st.markdown("""
    **To connect your organization:**
    1. Clone the repo
    2. Run `python setup.py` for guided setup
    3. Run `python validate_connections.py` to verify
    4. Run `python main.py` for the first live run
    """)