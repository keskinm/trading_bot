import json
import os.path
from pathlib import Path


cron_path = os.path.abspath(Path(__file__).parent / "cron.json")

with open("./test_crontab/cron.json", "r", encoding="utf-8") as fopen:
    data = json.load(fopen)
    data[0] = data[0] + 1

with open(cron_path, "w", encoding="utf-8") as fopen:
    json.dump(data, fopen)
