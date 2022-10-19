import os.path
import random
from pathlib import Path
import pandas as pd
from strategies.grid_spot_usd.strategy import GridTrader
from datetime import datetime
import json


class SimulatedGridTrader(GridTrader):
    def __init__(self):
        last_data_file_path = Path(os.path.abspath(Path(__file__).parent)) / "data"/ "simulated_last_data.json"
        super().__init__(last_data_file_path=last_data_file_path)

        self.simulated_exchange_file_path = Path(os.path.abspath(Path(__file__).parent)) / "data" / "simulated_exchange.json"
        with open(self.simulated_exchange_file_path, "r", encoding="utf-8") as fopen:
            self.simulated_exchange = json.load(fopen)
        self.coin1_balance = self.simulated_exchange["balances"]["coin1"]
        self.coin2_balance = self.simulated_exchange["balances"]["coin2"]
        self.consumer = Consumer()

    def run(self):
        now = datetime.now()
        print(now.strftime("%d-%m %H:%M:%S"))

        current_price = self.exchange.get_bid_ask_price(self.symbol)["bid"]

        orders_list = self.simulated_exchange["orders"]
        df_order = pd.DataFrame(orders_list)

        if df_order.empty == False:
            df_order["price"] = pd.to_numeric(df_order["price"])
            # df_order["size"] = pd.to_numeric(df_order["size"])
        # print(df_order)

        coin1_balance = self.exchange.get_detail_balance_of_one_coin(self.coin1)["free"]
        coin2_balance = self.exchange.get_detail_balance_of_one_coin(self.coin2)["free"]

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
                amount = (coin2_balance / current_price) / buy_order_to_create
                price = current_price - diff_buy * (i + 1)
                self.simulated_exchange["orders"].append({"price": price, "amount": amount, "side": "buy"})

            for i in range(sell_order_to_create):
                amount = coin1_balance / sell_order_to_create
                price = current_price + diff_sell * (i + 1)
                self.simulated_exchange["orders"].append({"price": price, "amount": amount, "side": "sell"})

        self.write_last_data()
        self.consumer.consume_orders()
        self.consumer.write_exchange()

    def consumed_grid(self, current_price):
        grid_buy, grid_sell = self.custom_grid(
            current_price,
            last_order_down=0.4,
            last_order_up=1.2,
            down_grid_len=5,
            up_grid_len=5,
        )
        for buy in grid_buy:
            amount = (self.coin2_balance / buy) / len(grid_buy)
            self.simulated_exchange["orders"].append({"price": buy, "amount": amount, "side": "buy"})

        for sell in grid_sell:
            amount = self.coin1_balance / len(grid_sell)
            self.simulated_exchange["orders"].append({"price": sell, "amount": amount, "side": "sell"})

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

        with open(self.simulated_exchange_file_path, "w") as outfile:
            json.dump(self.simulated_exchange, outfile)


class Consumer:
    def __init__(self):
        self.simulated_exchange = None
        self.simulated_exchange_file_path = Path(
            os.path.abspath(Path(__file__).parent)) / "data" / "simulated_exchange.json"

        with open(self.simulated_exchange_file_path, "r", encoding="utf-8") as fopen:
            self.simulated_exchange = json.load(fopen)
        self.coin1_balance = self.simulated_exchange["balances"]["coin1"]
        self.coin2_balance = self.simulated_exchange["balances"]["coin2"]

    def consume_orders(self):
        consumed_orders = []

        nb_consume = random.randint(0, len(self.simulated_exchange["orders"]))
        for idx in range(nb_consume):
            consumed = self.simulated_exchange["orders"][idx]
            consumed_orders.append(consumed)

            if consumed["side"] == "buy":
                self.coin1_balance += consumed["amount"]
                self.coin2_balance -= consumed["price"] * consumed["amount"]

            if consumed["side"] == "sell":
                self.coin1_balance -= consumed["amount"]
                self.coin2_balance += consumed["price"] * consumed["amount"]

        self.simulated_exchange["orders"] = list(set(self.simulated_exchange["orders"]) - set(consumed_orders))

    def write_exchange(self):
        self.simulated_exchange["balances"]["coin1"] = self.coin1_balance
        self.simulated_exchange["balances"]["coin2"] = self.coin2_balance

        with open(self.simulated_exchange_file_path, "w") as outfile:
            json.dump(self.simulated_exchange, outfile)


def run():
    SimulatedGridTrader().run()
