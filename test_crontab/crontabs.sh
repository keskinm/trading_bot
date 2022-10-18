BOT_WD=/home/mustafa-cleverdoc/PycharmProjects/trading_bot/
VENV=/home/mustafa-cleverdoc/PycharmProjects/trading_bot/venv-3.9.12
echo ---- >> $BOT_WD/cronlog.log
cd $BOT_WD && echo CD DONE >> $BOT_WD/test_crontab/cronlog.log && $VENV/bin/python -m test_crontab.test_crontab_run >> $BOT_WD/test_crontab/cronlog.log 2>&1
