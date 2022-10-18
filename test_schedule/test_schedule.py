import json
import os
import signal
import psutil
from pathlib import Path

import schedule

import time

from daemon import Daemon, AdvancedDaemon


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
    time.sleep(0.5)
    with open(values_file_path, "r", encoding="utf-8") as fopen:
        data = json.load(fopen)
        data[0] = data[0] + 1
        # try:
        #     data = json.load(fopen)
        #     data[0] = data[0] + 1
        # except json.decoder.JSONDecodeError as err:
        #     x = fopen.readlines()
        #     print("DATA", x)
        #     time.sleep(10000)
        #     raise ValueError

    with open(values_file_path, "w", encoding="utf-8") as fopen:
        json.dump(data, fopen)


class IncreaseValues(AdvancedDaemon):
    def __init__(self, pidfile, values_file_path):
        super().__init__(pidfile)
        self.initial_value = create_increase_value_file_path(values_file_path)
        self.values_file_path = values_file_path

    def at_finish_cb(self):
        time.sleep(1)
        with open(self.values_file_path, "r", encoding="utf-8") as fopen:
            final_value = json.load(fopen)
        assert final_value > self.initial_value
        # with open(self.pidfile, "r", encoding="utf-8") as fopen:
        #     to_kill_pid = int(fopen.readlines()[-1])
        #     if psutil.pid_exists(to_kill_pid):
        #         # Should be done by Daemon if child finished (won't be done if infinite loop !)
        #         os.kill(to_kill_pid, signal.SIGTERM)
        #     assert psutil.pid_exists(to_kill_pid)

    def run(self):
        for i in range(10):
            increase_value(self.values_file_path)
        self.at_finish_cb()


class ScheduledIncreaseValue(AdvancedDaemon):
    def __init__(self, pidfile, values_file_path):
        super().__init__(pidfile)
        self.initial_value = create_increase_value_file_path(values_file_path)
        self.values_file_path = values_file_path

    def at_finish_cb(self):
        time.sleep(1)
        with open(self.values_file_path, "r", encoding="utf-8") as fopen:
            final_value = json.load(fopen)
        assert final_value > self.initial_value
        # with open(self.pidfile, "r", encoding="utf-8") as fopen:
        #     to_kill_pid = int(fopen.readlines()[-1])
        #     if psutil.pid_exists(to_kill_pid):
        #         # Should be done by Daemon if child finished (won't be done if infinite loop !)
        #         os.kill(to_kill_pid, signal.SIGTERM)
        #     assert psutil.pid_exists(to_kill_pid)

    def run(self):
        schedule.every(1).seconds.do(increase_value, values_file_path=self.values_file_path)

        t_end = time.time() + 5
        while time.time() < t_end:
            schedule.run_pending()
        self.at_finish_cb()


def test_increase_values():
    values_file_path = Path(os.path.abspath(Path(__file__).parent / "test_increase_value.json"))

    pid_file_path = os.path.abspath(Path(__file__).parent / "to_kill_ids" / "test_increase_values.txt")

    b_runner = IncreaseValues(pidfile=pid_file_path, values_file_path=values_file_path)
    b_runner.start()


def test_scheduled_increase_values():
    values_file_path = Path(os.path.abspath(Path(__file__).parent / "test_scheduled_increase_value.json"))
    pid_file_path = os.path.abspath(Path(__file__).parent / "to_kill_ids" / "test_scheduled_increase_values.txt")

    b_runner = ScheduledIncreaseValue(pidfile=pid_file_path, values_file_path=values_file_path)
    b_runner.start()

test_scheduled_increase_values()
