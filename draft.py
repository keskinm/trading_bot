import ccxt
import pandas as pd
from utilities.spot_ftx import SpotFtx
from datetime import datetime
import time
import json

f = open(
    "./secret.json",
)
secret = json.load(f)
f.close()

account_to_select = "account1"


ftx = SpotFtx(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    subAccountName=secret[account_to_select]["subAccountName"],
)

symbol = "BTC/EUR"

current_price = ftx.get_bid_ask_price(symbol)["bid"]
current_price

# ftx.place_limit_order(
#     symbol=symbol,
#     side="buy",
#     amount=(coin2_balance / current_price) / buy_order_to_create,
#     price=current_price-0.1*current_price,
# )

