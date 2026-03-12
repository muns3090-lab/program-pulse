import requests
from requests.auth import HTTPBasicAuth
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()


class ConfluenceClient:
    def __init__(self, config):
        self.base_url = config["confluence"]["base_url"]
        self.email = config["jira"]["email"]
        self.token = os.getenv("JIRA_API_TOKEN")
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self.page_id = config["confluence"]["status_page_id"]

    def test_connection(self):
        url = f"{self.base_url}/rest/api/content/{self.page_id}"
        r = requests.get(url, auth=self.auth, headers=self.headers)
        return r.status_code == 200

    def get_page_version(self):
        url = f"{self.base_url}/rest/api/content/{self.page_id}?expand=version"
        r = requests.get(url, auth=self.auth, headers=self.headers)
        r.raise_for_status()
        return r.json()["version"]["number"]

    def update_status_page(self, epics_summary):
        version = self.get_page_version()
        rows = ""
        for epic in epics_summary:
            color = {"On Track": "#36B37E", "At Risk": "#FF991F", "Overdue": "#FF5630"}.get(epic["status"], "#6B778C")
            rows += f"""
            <tr>
                <td>{epic['key']}</td>
                <td>{epic['summary']}</td>
                <td>{epic['assignee']}</td>
                <td>{epic['due_date']}</td>
                <td><span style="color:{color};font-weight:bold;">{epic['status']}</span></td>
                <td>{epic.get('notes', '')}</td>
            </tr>"""

        html = f"""
        <h2>Program Health Status — Last updated: {date.today()}</h2>
        <table>
            <thead><tr>
                <th>Key</th><th>Epic/Story</th><th>Assignee</th>
                <th>Due Date</th><th>Status</th><th>Notes</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table>"""

        url = f"{self.base_url}/rest/api/content/{self.page_id}"
        payload = {
            "version": {"number": version + 1},
            "title": "Program Pulse — Status Dashboard",
            "type": "page",
            "body": {"storage": {"value": html, "representation": "storage"}}
        }
        r = requests.put(url, json=payload, auth=self.auth, headers=self.headers)
        return r.status_code == 200