import datetime

import requests

SERVER_URL = "http://localhost:5000/alert"


def calculate_severity(threat_votes):
    if threat_votes >= 3:
        return "CRITICAL"
    if threat_votes == 2:
        return "HIGH"
    if threat_votes == 1:
        return "MODERATE"
    return "LOW"


def send_alert(threat_votes, source="AI Threat Detection"):
    payload = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "threat_votes": threat_votes,
        "severity": calculate_severity(threat_votes),
        "source": source,
    }

    try:
        response = requests.post(SERVER_URL, json=payload, timeout=3)
        if response.ok:
            return True, f"Alert delivered to {SERVER_URL} with severity {payload['severity']}."
        return False, f"Alert endpoint responded with status {response.status_code}."
    except requests.RequestException as exc:
        return False, f"Alert delivery failed: {exc}"
