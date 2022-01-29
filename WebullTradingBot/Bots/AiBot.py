import pandas as pd

from datetime import datetime
from datetime import timezone

from enum import Enum

from typing import List
from typing import Dict
from typing import Union

from Objects.Trades import Trade
from Objects.Portfolios import Portfolio
from Objects.StockFrame import StockFrame
from Bots.TradingBot import TradingBot

class AiBot():
    class Market_Type(Enum):
        """Webull uses NYSE for trades which is on eastern
        standard time"""
        not_opened = 0 # 8pm - 4am 
        pre_market = 1 # 4am - 6:30am
        market = 2 # 6:30am - 4pm
        post_market = 3 # 4pm - 8pm

    def __init__(self, trading_account: str = None, trading_bot: TradingBot = None):
        self.trading_account = trading_account
        self.trades = {}
        self.stock_frame: StockFrame = None
        self.Market_Type = AiBot.Market_Type.not_opened

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
            self.Market_Type = AiBot.Market_Type.post_market
            self.monitor_post_market()
        elif self.__trading_bot__.market_open():
            self.Market_Type = AiBot.Market_Type.market
            self.monitor_market()
        elif self.__trading_bot__.pre_market_open():
            self.Market_Type = AiBot.Market_Type.pre_market
            self.monitor_pre_market()

    def monitor_pre_market(self):
        """Automates and monitors the buying and selling
        of pre-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        if self.__trading_bot__.is_logged_in:
            __monitor_markets()
        
    def monitor_market(self):
        """Automates and monitors the buying and selling
        of regular-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        if self.__trading_bot__.is_logged_in:
            __monitor_markets

    def monitor_post_market(self):
        """Automates and monitors the buying and selling
        of post-market stocks.
        """
        if self.__trading_bot__ is None:
            raise Exception("Trading bot is not initialized. Ai bot cannot continue.")

        if self.__trading_bot__.is_logged_in:
            __monitor_markets

    def run_market_async(self):
        """Starts the monitor market loop, checking for
        market times and performing trades
        """
        from Utils.MultiProcessing import MultiProcess
        process = MultiProcess()
        process.run(self.__monitor_markets)

    def __monitor_markets(self):
        """This monitors the actual market by using a while loop
        method from an async parallel call while the user is free
        to use commands. It is a private method only and called only
        by setup_market_async.
        """
        while self.__trading_bot__.is_logged_in:

            # Make sure to check which market is opened and adjust accordingly
            if self.__trading_bot__.post_market_open():
                self.Market_Type = AiBot.Market_Type.post_market
            elif self.__trading_bot__.market_open():
                self.Market_Type = AiBot.Market_Type.market
            elif self.__trading_bot__.pre_market_open():
                self.Market_Type = AiBot.Market_Type.pre_market
            else:
                self.Market_Type = AiBot.Market_Type.not_opened
                print("Markets are closed. AI bot will not perform functions until a market opens.")
                # TODO add a timer here with a length based on the amount of time remaining until pre-market opens