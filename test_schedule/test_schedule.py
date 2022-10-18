import json
import os
from pathlib import Path

import schedule

import time

from daemon import Daemon


def increase_value():
    time.sleep(2)
    values_file_path = Path(os.path.abspath(Path(__file__).parent / "schedule.json"))
    if not os.path.exists(values_file_path):
        with open(values_file_path, "w", encoding="utf-8") as fopen:
            json.dump([0], fopen)

    with open(values_file_path, "r", encoding="utf-8") as fopen:
        data = json.load(fopen)
        data[0] = data[0] + 1

    with open(values_file_path, "w", encoding="utf-8") as fopen:
        json.dump(data, fopen)


class IncreaseValues(Daemon):
    def __init__(self, pidfile):
        super().__init__(pidfile)

    def run(self):
        while True:
            increase_value()


class ScheduledIncreaseValue(Daemon):
    def __init__(self, pidfile):
        super().__init__(pidfile)

    def run(self):
        schedule.every(1).seconds.do(increase_value())

        while True:
            schedule.run_pending()


def test_increase_values():
    b_runner = IncreaseValues(pidfile="./to_kill_ids.txt")
    b_runner.start()


def test_scheduled_increase_values():
    b_runner = ScheduledIncreaseValue(pidfile="./to_kill_ids.txt")
    b_runner.start()


test_scheduled_increase_values()
