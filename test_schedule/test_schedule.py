import json
import os
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
        """
        try:
            data = json.load(fopen)
            data[0] = data[0] + 1
        except json.decoder.JSONDecodeError as err:
            x = fopen.readlines()
            print("DATA", x)
            time.sleep(10000)
            raise ValueError
        """

    with open(values_file_path, "w", encoding="utf-8") as fopen:
        json.dump(data, fopen)


class IncreaseValues(NonExitingDaemon):
    def __init__(self, work_dir_path):
        super().__init__(work_dir_path=work_dir_path)
        values_file_path = work_dir_path / "test_increase_value.json"
        self.initial_value = create_increase_value_file_path(values_file_path)
        self.values_file_path = values_file_path

    def at_finish_assert(self):
        time.sleep(1)
        with open(self.values_file_path, "r", encoding="utf-8") as fopen:
            final_value = json.load(fopen)
        self.asserted = (final_value > self.initial_value)

    def run(self):
        for i in range(10):
            try:
                increase_value(self.values_file_path)
            except BaseException as e:
                self.trace_back.append(repr(e))

        self.at_finish_assert()
        with open(self.log_file_path, "a", encoding="utf-8") as fopen:
            for err_msg in self.trace_back:
                fopen.write(f"{err_msg}\n\n-------------------------\n\n")


class ScheduledIncreaseValue(Daemon):
    def __init__(self, work_dir_path):
        super().__init__(work_dir_path=work_dir_path)
        values_file_path = work_dir_path / "test_scheduled_increase_value.json"
        self.initial_value = create_increase_value_file_path(values_file_path)
        self.values_file_path = values_file_path

    def run(self):
        schedule.every(1).seconds.do(increase_value, values_file_path=self.values_file_path)

        t_end = time.time() + 5
        while time.time() < t_end:
            try:
                schedule.run_pending()
            except BaseException as e:
                self.trace_back.append(repr(e))

        with open(self.log_file_path, "a", encoding="utf-8") as fopen:
            for err_msg in self.trace_back:
                fopen.write(f"{err_msg}\n\n-------------------------\n\n")


def t_increase_values():
    """Note that non exiting parent process make happens totally unexpected behaviors.

    A mysterious JSONDecode Error is appearing.
    Test of this function is duplicated with multiple pass/fail (maybe making
    multiple other function tests also).
    Please prefer to test daemonized jobs with run(), inheriting classic
    parent process exiting Daemon class.
    """
    work_dir_path = Path(os.path.abspath(Path(__file__).parent / "test_increase_values"))

    b_runner = IncreaseValues(work_dir_path=work_dir_path)
    b_runner.start()
    assert b_runner.asserted


def test_scheduled_increase_values():
    """Tested with run."""
    work_dir_path = Path(os.path.abspath(Path(__file__).parent / "test_scheduled_increase_values"))

    b_runner = ScheduledIncreaseValue(work_dir_path=work_dir_path)
    b_runner.run()

    with open(b_runner.values_file_path, "r", encoding="utf-8") as fopen:
        final_value = json.load(fopen)
    assert final_value > b_runner.initial_value
