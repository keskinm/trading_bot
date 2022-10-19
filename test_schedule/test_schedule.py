import json
import os
import signal
import psutil
from pathlib import Path

import schedule

import time

from daemon import Daemon, NonExitingDaemon


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


class IncreaseValues(NonExitingDaemon):
    def __init__(self, work_dir_path):
        super().__init__(work_dir_path=work_dir_path)
        values_file_path = work_dir_path / "test_increase_value.json"
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
            try:
                increase_value(self.values_file_path)
            except BaseException as e:
                self.trace_back.append(repr(e))

        self.at_finish_cb()
        with open(self.log_file_path, "a", encoding="utf-8") as fopen:
            for err_msg in self.trace_back:
                fopen.write(f"{err_msg}\n\n-------------------------\n\n")


class ScheduledIncreaseValue(NonExitingDaemon):
    def __init__(self, work_dir_path):
        super().__init__(work_dir_path=work_dir_path)
        values_file_path = work_dir_path / "test_scheduled_increase_value.json"
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
            try:
                schedule.run_pending()
            except BaseException as e:
                self.trace_back.append(repr(e))

        self.at_finish_cb()
        with open(self.log_file_path, "a", encoding="utf-8") as fopen:
            for err_msg in self.trace_back:
                fopen.write(f"{err_msg}\n\n-------------------------\n\n")


def test_increase_values():
    work_dir_path = Path(os.path.abspath(Path(__file__).parent / "test_increase_values"))

    b_runner = IncreaseValues(work_dir_path=work_dir_path)
    b_runner.start()


def test_scheduled_increase_values():
    work_dir_path = Path(os.path.abspath(Path(__file__).parent / "test_scheduled_increase_values"))

    b_runner = ScheduledIncreaseValue(work_dir_path=work_dir_path)
    b_runner.start()
