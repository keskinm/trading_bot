import json
import os
import time
from pathlib import Path

from crontab import CronTab
import pytest

increase_value_file_path = os.path.abspath(Path(__file__).parent / "increase_value.json")


@pytest.mark.skipif(os.getenv("skip_long_tests"), reason="Skipping long tests.")
def test_crontab():
    parent_abs_dir = Path(os.path.abspath(Path(__file__).parent))
    log_path = parent_abs_dir / "cronlog.log"

    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as fopen:
            fopen.write("")

    if not os.path.exists(increase_value_file_path):
        initial_value = 0
        with open(increase_value_file_path, "w", encoding="utf-8") as fopen:
            json.dump([initial_value], fopen)
    else:
        with open(increase_value_file_path, "r", encoding="utf-8") as fopen:
            initial_value = json.load(fopen)[0]

    cron = CronTab(os.environ.get("USERNAME"))
    job = cron.new(command="sh " + str(parent_abs_dir / "crontabs.sh"))
    job.minute.every(1)
    cron.write()
    time.sleep(65)

    with open(increase_value_file_path, "r", encoding="utf-8") as fopen:
        assert json.load(fopen)[0] > initial_value

    assert os.path.getsize(log_path)
    cron.remove(job)
