import os
from pathlib import Path

from crontab import CronTab

parent_abs_dir = Path(os.path.abspath(Path(__file__).parent))
log_path = parent_abs_dir / "cronlog.log"

if not os.path.exists(log_path):
    with open(log_path, "w", encoding="utf-8") as fopen:
        fopen.write("")

cron = CronTab(os.environ.get("USERNAME"))
job = cron.new(command="sh " + str(parent_abs_dir / "crontabs.sh"))
job.minute.every(1)
cron.write()

