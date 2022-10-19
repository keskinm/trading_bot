from strategies.grid_spot_usd.strategy_plain import run
import schedule
import time


schedule.every(1).seconds.do(run)


while True:
    schedule.run_pending()
    time.sleep(1)
