"""
Poll GitHub API for latest workflow run per agent and sync 'quality' field.
Run manually or via cron until webhooks are wired.
"""
import os, requests, datetime, sqlite_utils, time

GITHUB_REPO = "the-emergence-ai/EmergenceHQ"
DIR = "http://127.0.0.1:8000"
TOKEN = os.getenv("GH_PAT")  # personal-access token with 'repo' scope
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

def fetch_quality(agent):
    url = (f"https://api.github.com/repos/{GITHUB_REPO}"
           f"/actions/workflows/agent-validation.yml/runs"
           f"?branch={agent}&per_page=1")
    r = requests.get(url, headers=HEADERS, timeout=10).json()
    if not r.get("workflow_runs"):
        return None
    status = r["workflow_runs"][0]["conclusion"]  # success / failure / null
    return "pass" if status == "success" else "fail"

def loop():
    while True:
        agents = requests.get(f"{DIR}/agents").json()
        for a in agents:
            q = fetch_quality(a["name"])
            if q:
                requests.patch(f"{DIR}/agents/{a['name']}",
                               json={"quality": q})
        time.sleep(300)   # every 5 min

if __name__ == "__main__":
    loop()
