from strategies.grid_spot_usd.simul_strategy import run
import schedule
import time


schedule.every(10).seconds.do(run)


while True:
    schedule.run_pending()
    time.sleep(1)
