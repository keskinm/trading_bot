import json
import os
from pathlib import Path

import schedule

import time

from daemon import Daemon


def create_increase_value_file_path(values_file_path):
    if not os.path.exists(values_file_path):
        data = [0]
        with open(values_file_path, "w", encoding="utf-8") as fopen:
            json.dump(data, fopen)
    else:
        with open(values_file_path, "r", encoding="utf-8") as fopen:
            data = json.load(fopen)
    return data


def increase_value(values_file_path):
    time.sleep(2)
    with open(values_file_path, "r", encoding="utf-8") as fopen:
        data = json.load(fopen)
        data[0] = data[0] + 1

    with open(values_file_path, "w", encoding="utf-8") as fopen:
        json.dump(data, fopen)


class IncreaseValues(Daemon):
    def __init__(self, pidfile, values_file_path):
        super().__init__(pidfile)
        self.values_file_path = values_file_path

    def run(self):
        while True:
            increase_value(self.values_file_path)


class ScheduledIncreaseValue(Daemon):
    def __init__(self, pidfile, values_file_path):
        super().__init__(pidfile)
        self.values_file_path = values_file_path

    def run(self):
        schedule.every(1).seconds.do(increase_value, values_file_path=self.values_file_path)

        while True:
            schedule.run_pending()


def test_increase_values():
    values_file_path = Path(os.path.abspath(Path(__file__).parent / "test_increase_value.json"))
    initial_value = create_increase_value_file_path(values_file_path)
    b_runner = IncreaseValues(pidfile="./to_kill_ids.txt", values_file_path=values_file_path)
    b_runner.start()
    time.sleep(3)
    with open(values_file_path, "r", encoding="utf-8") as fopen:
        final_value = json.load(fopen)
    assert final_value > initial_value


def test_scheduled_increase_values():
    values_file_path = Path(os.path.abspath(Path(__file__).parent / "test_scheduled_increase_value.json"))
    initial_value = create_increase_value_file_path(values_file_path)
    b_runner = ScheduledIncreaseValue(pidfile="./to_kill_ids.txt", values_file_path=values_file_path)
    b_runner.start()
    time.sleep(3)
    with open(values_file_path, "r", encoding="utf-8") as fopen:
        final_value = json.load(fopen)
    assert final_value > initial_value


test_scheduled_increase_values()
