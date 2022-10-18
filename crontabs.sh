#BOT_WD=/home/mustafa-cleverdoc/PycharmProjects/trading_bot
#VENV=venv-3.9.12
#*/1 * * * * echo ---- >> $BOT_WD/cronlog.log
#*/1 * * * * cd $BOT_WD && echo CD DONE >> cronlog.log && $VENV/bin/python -m test_crontab.test_crontab >> cronlog.log 2>&1
