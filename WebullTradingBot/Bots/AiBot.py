import pandas as pd

from datetime import datetime
from datetime import timezone

from typing import List
from typing import Dict
from typing import Union

from Objects.Trades import Trade
from Objects.Portfolios import Portfolio
from Objects.StockFrame import StockFrame
from Bots.TradingBot import TradingBot

class AiBot():
    def __init__(self, trading_account: str = None, trading_bot: TradingBot = None):
        self.trading_account = trading_account
        self.trades = {}
        self.stock_frame = None

        self.__trading_bot__ = trading_bot

    def initiate_session(self):
        """Starts a new session and initiates
        the automated bot to monitor the stock market
        """
        if self.__trading_bot__ is None:
            print("Trading bot has not been created and initialized yet. Cannot start the Ai Bot.")
            return

        # Figure out which to monitor
        if self.__trading_bot__.post_market_open():
            self.monitor_post_market()
        elif self.__trading_bot__.market_open():
            self.monitor_market()
        elif self.__trading_bot__.pre_market_open():
            self.monitor_pre_market()

    def monitor_pre_market(self):
        """Automates and monitors the buying and selling
        of pre-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        while self.__trading_bot__.is_logged_in:
            pass

    def monitor_market(self):
        """Automates and monitors the buying and selling
        of regular-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        while self.__trading_bot__.is_logged_in:
            pass

    def monitor_post_market(self):
        """Automates and monitors the buying and selling
        of post-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        while self.__trading_bot__.is_logged_in:
            pass