import schedule
import time


def task():
    print("Job Executing!")


schedule.every(1).seconds.do(task)


while True:
    schedule.run_pending()
    time.sleep(1)
