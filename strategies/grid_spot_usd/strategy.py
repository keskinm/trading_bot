import os.path
from pathlib import Path

import pandas as pd
from utilities.spot_ftx import SpotFtx
from datetime import datetime
import json


class GridTrader:
    def __init__(self, last_data_file_path=None):
        if last_data_file_path is None:
            last_data_file_path = Path(os.path.abspath(Path(__file__).parent)) / "data" / "last_data.json"

        self.last_data_file_path = last_data_file_path

        with open(self.last_data_file_path, "r", encoding="utf-8") as fopen:
            self.last_data = json.load(fopen)

        with open("./secret.json", "r", encoding="utf-8") as fopen:
            secret = json.load(fopen)

        account_to_select = "account1"

        self.exchange = SpotFtx(
                apiKey=secret[account_to_select]["apiKey"],
                secret=secret[account_to_select]["secret"],
                subAccountName=secret[account_to_select]["subAccountName"],
            )

        self.coin1 = "DOGE"
        self.coin2 = "USD"
        self.symbol = f"{self.coin1}/{self.coin2}"
        self.coin1_balance = self.exchange.get_detail_balance_of_one_coin(self.coin1)["free"]
        self.coin2_balance = self.exchange.get_detail_balance_of_one_coin(self.coin2)["free"]

        self.total_orders = 10

        self.orders_list = []
        for order in self.exchange.get_open_order():
            self.orders_list.append(order["info"])

    @staticmethod
    def custom_grid(
            first_price, last_order_down=0.5, last_order_up=1, down_grid_len=10, up_grid_len=10
    ):
        down_pct_unity = last_order_down / down_grid_len
        up_pct_unity = last_order_up / up_grid_len

        grid_sell = []
        grid_buy = []

        for i in range(down_grid_len):
            grid_buy.append(first_price - first_price * down_pct_unity * (i + 1))

        for i in range(up_grid_len):
            grid_sell.append(first_price + first_price * up_pct_unity * (i + 1))

        return grid_buy, grid_sell

    def run(self):
        now = datetime.now()
        print(now.strftime("%d-%m %H:%M:%S"))

        try:
            current_price = self.exchange.get_bid_ask_price(self.symbol)["bid"]
        except BaseException as err:
            print("An error occured @ get bid ask @ strategy @ run", err)
            exit()

        df_order = pd.DataFrame(self.orders_list)

        if df_order.empty == False:
            df_order["price"] = pd.to_numeric(df_order["price"])
            df_order["size"] = pd.to_numeric(df_order["size"])
        # print(df_order)

        # print(coin1_balance, coin2_balance)

        if (
                df_order.empty
                or len(df_order.loc[df_order["side"] == "buy"]) == 0
                or len(df_order.loc[df_order["side"] == "sell"]) == 0
        ):
            self.consumed_grid(current_price)

        elif self.total_orders == len(df_order):
            print("no new orders")

        else:
            buy_order_to_create = self.last_data["number_of_sell_orders"] - len(
                df_order.loc[df_order["side"] == "sell"]
            )
            sell_order_to_create = self.last_data["number_of_buy_orders"] - len(
                df_order.loc[df_order["side"] == "buy"]
            )
            print("Create", buy_order_to_create, "new buy orders")
            print("Create", sell_order_to_create, "new sell orders")
            last_buy_order = df_order.loc[df_order["side"] == "buy"]["price"].max()
            last_sell_order = df_order.loc[df_order["side"] == "sell"]["price"].min()

            diff_buy = (current_price - last_buy_order) / (buy_order_to_create + 1)
            diff_sell = (last_sell_order - current_price) / (sell_order_to_create + 1)

            for i in range(buy_order_to_create):
                # print("buy",current_price - diff_buy*(i+1))
                self.exchange.place_limit_order(
                    symbol=self.symbol,
                    side="buy",
                    amount=(self.coin2_balance / current_price) / buy_order_to_create,
                    price=current_price - diff_buy * (i + 1),
                )
            for i in range(sell_order_to_create):
                # print("sell",current_price + diff_sell*(i+1))
                self.exchange.place_limit_order(
                    symbol=self.symbol,
                    side="sell",
                    amount=self.coin1_balance / sell_order_to_create,
                    price=current_price + diff_sell * (i + 1),
                )

        self.write_last_data()

    def consumed_grid(self, current_price):
        print("create new grid")
        grid_buy, grid_sell = self.custom_grid(
            current_price,
            last_order_down=0.4,
            last_order_up=1.2,
            down_grid_len=5,
            up_grid_len=5,
        )
        for buy in grid_buy:
            # print(buy,(coin2_balance/buy)/len(grid_buy))
            self.exchange.place_limit_order(
                symbol=self.symbol,
                side="buy",
                amount=(self.coin2_balance / buy) / len(grid_buy),
                price=buy,
            )
        for sell in grid_sell:
            # print(sell,coin1_balance/len(grid_sell))
            self.exchange.place_limit_order(
                symbol=self.symbol,
                side="sell",
                amount=self.coin1_balance / len(grid_sell),
                price=sell,
            )

    def write_last_data(self):
        df_order = pd.DataFrame(self.orders_list)

        if df_order.empty == False:
            self.last_data["number_of_buy_orders"] = len(df_order.loc[df_order["side"] == "buy"])
            self.last_data["number_of_sell_orders"] = len(df_order.loc[df_order["side"] == "sell"])
        else:
            self.last_data["number_of_buy_orders"] = 0
            self.last_data["number_of_sell_orders"] = 0
        with open(self.last_data_file_path, "w") as outfile:
            json.dump(self.last_data, outfile)


def run():
    GridTrader().run()
