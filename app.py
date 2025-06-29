from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import os
app = Flask(__name__)

REDMINE_URL = os.environ['REDMINE_URL']
API_KEY = os.environ['API_KEY']
PROJECT_ID = os.environ['PROJECT_ID']
Track_ID = os.environ['Track_ID']
# スケジュール読み込み
with open("schedule.json", "r", encoding="utf-8") as f:
    SCHEDULE = json.load(f)

# 担当者決定
def get_current_assignee():
    now = datetime.now()
    weekday = now.strftime("%A")  # Monday, Tuesday, ...
    current_time = now.time()

    if weekday in SCHEDULE:
        for time_range, user_id in SCHEDULE[weekday].items():
            start_str, end_str = time_range.split('-')
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()
            if start <= current_time <= end:
                return user_id
    return None

# アラート受信エンドポイント
@app.route('/alert', methods=['POST'])
def create_redmine_issue():
    data = request.json
    alerts = data.get("alerts", [])

    assigned_user_id = get_current_assignee()
    if not assigned_user_id:
        print("⚠️ 時間外または該当者なし。チケットは作成されません。")
        return jsonify({"status": "no_assignee"}), 200

    for alert in alerts:
        subject = f"[Alert] {alert['labels'].get('alertname', 'NoAlertName')}"
        description = alert['annotations'].get('description', 'No description')

        issue_data = {
            "issue": {
                "project_id": PROJECT_ID,
                "subject": subject,
                "description": description,
                "tracker_id": Track_ID,
                "priority_id": 4,
                "assigned_to_id": assigned_user_id
            }
        }

        res = requests.post(
            f"{REDMINE_URL}/issues.json",
            json=issue_data,
            headers={
                'X-Redmine-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        )

        if res.status_code != 201:
            print("❌ チケット作成失敗:", res.text)

    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

