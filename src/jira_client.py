import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()


class JiraClient:
    def __init__(self, config):
        self.base_url = config["jira"]["base_url"]
        self.email = config["jira"]["email"]
        self.token = os.getenv("JIRA_API_TOKEN")
        self.auth = HTTPBasicAuth(self.email, self.token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.project_keys = config["jira"]["project_keys"]
        self.at_risk_label = config["jira"].get("at_risk_label", "AT-RISK")

    def test_connection(self):
        url = f"{self.base_url}/rest/api/3/myself"
        r = requests.get(url, auth=self.auth, headers=self.headers)
        return r.status_code == 200, r.json()

    def get_epics_and_stories(self):
        projects = " OR ".join([f'project = "{k}"' for k in self.project_keys])
        jql = (
            f'({projects}) AND issuetype in (Epic, Story) '
            f'AND due is not EMPTY ORDER BY due ASC'
        )
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": 200,
            "fields": (
                "summary,assignee,duedate,status,priority,"
                "description,comment,labels,issuetype,parent"
            )
        }
        r = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json().get("issues", [])

    def get_last_comment_date(self, issue_key: str) -> date | None:
        """Returns the date of the last comment, or None."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        r = requests.get(url, auth=self.auth, headers=self.headers)
        comments = r.json().get("comments", [])
        if not comments:
            return None
        last = comments[-1]["created"]
        return datetime.fromisoformat(last[:10]).date()

    def get_last_comment_text(self, issue_key: str) -> str:
        """Returns the plain text of the last comment, or empty string."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        r = requests.get(url, auth=self.auth, headers=self.headers)
        comments = r.json().get("comments", [])
        if not comments:
            return ""
        last_comment = comments[-1]
        # Extract text from Atlassian Document Format (ADF)
        body = last_comment.get("body", {})
        if isinstance(body, str):
            return body[:500]
        # ADF format — extract text nodes
        texts = []
        for block in body.get("content", []):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    texts.append(inline.get("text", ""))
        return " ".join(texts)[:500]

    def add_label(self, issue_key: str, label: str):
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        payload = {"update": {"labels": [{"add": label}]}}
        r = requests.put(url, json=payload, auth=self.auth, headers=self.headers)
        return r.status_code == 204

    def add_comment(self, issue_key: str, message: str):
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": message}]
                }]
            }
        }
        r = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        return r.status_code == 201