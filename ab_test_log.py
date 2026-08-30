import json
from datetime import datetime

LOG_FILE = "ab_test_logs.json"

def write_ab_log(data):
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(data)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)