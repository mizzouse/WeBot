import pandas as pd

from webull import webull
from webull import paper_webull

from datetime import datetime
from datetime import timezone

from typing import List
from typing import Dict
from typing import Union

from enum import Enum
from Utils.Enums import Login
from Objects.Trades import Trade
from Objects.Portfolios import Portfolio
from Objects.StockFrame import StockFrame

class TradingBot():
    def __init__(self, trading_account: str = None, paper_trading: bool = True):
        self.client_id: str = None
        self.trading_account = trading_account
        self.paper_trading = paper_trading
        self.trades = {}
        self.stock_frame: StockFrame = None
        self.LogType = Login.default

        self.token_expireTime = None

        self.__webull_client__ = None
        
    def _create_session(self, username: str, password: str, device_name = '', mfa = '', question_id = '', question_answer = '') -> bool:
        """Start a new session.
        Creates a new session with the Webull API and logs the user into
        the new session using only a username and password.
        This is for non-authenticated accounts or authenticated accounts
        that have gone through multi-factor authentications.
        Returns:
        ----
        True if successful, false otherwise.
        """

        # Create a new instance of the client
        if self.paper_trading == True:
            self.__webull_client__ = paper_webull()
        else:
            self.__webull_client__ = webull()

        # Log the client into the new session
        if mfa != '':
            self.__webull_client__.login(username, password, device_name, mfa, question_id, question_answer)
        else:
            self.__webull_client__.login(username, password)

        # Are we logged in?
        if self.__webull_client__.is_logged_in() == True:
            self.LogType = Login.LoggedIn

            self.token_expireTime = datetime.strptime(self.__webull_client__._token_expire, "%Y-%m-%dT%H:%M:%S.%f%z")
            return True
        else:
            self.LogType = Login.LoggedOut
            return False

    def create_portfolio(self) -> Portfolio:
        """Create a new portfolio.
        Creates a Portfolio Object to help store and organize positions
        as they are added and removed during trading.
        Usage:
        ----
            >>> portfolio = trading_bot.create_portfolio()
            >>> portfolio
            <bot.portfolio.Portfolio object at 0x0392BF88>
        Returns:
        ----
        Portfolio -- A bot.Portfolio object with no positions.
        """

        # Initalize the portfolio.
        self.portfolio = Portfolio(account_number = self.trading_account)

        # Assign the Client
        self.portfolio.webull_client(self.__webull_client__)

        return self.portfolio

    def create_trade(self, trade_id: str, enter_or_exit: str, long_or_short: str, order_type: str = 'mkt', price: float = 0.0, stop_limit_price = 0.0) -> Trade:
        """Initalizes a new instance of a Trade Object.
        This helps simplify the process of building an order by using pre-built templates that can be
        easily modified to incorporate more complex strategies.
        Arguments:
        ----
        trade_id {str} -- The ID associated with the trade, this can then be used to access the trade during runtime.
        enter_or_exit {str} -- Defines whether this trade will be used to enter or exit a position.
            If used to enter, specify `enter`. If used to exit, speicfy `exit`.
        long_or_short {str} -- Defines whether this trade will be used to go long or short a position.
            If used to go long, specify `long`. If used to go short, speicfy `short`.
        Keyword Arguments:
        ----
        order_type {str} -- Defines the type of order to initalize. Possible values
            are `'mkt', 'lmt', 'stop', 'stop-lmt', 'trailign-stop'` (default: {'mkt'})
        price {float} -- The Price to be associate with the order. If the order type is `stop` or `stop-lmt` then
            it is the stop price, if it is a `lmt` order then it is the limit price, and `mkt` is the market
            price.(default: {0.0})
        stop_limit_price {float} -- Only used if the order is a `stop-lmt` and represents the limit price of
            the `stop-lmt` order. (default: {0.0})
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
            )
            >>> new_trade = trading_robot_portfolio.create_trade(
                trade_id='long_1',
                enter_or_exit='enter',
                long_or_short='long',
                order_type='mkt'
            )
            >>> new_trade
            >>> new_market_trade = trading_robot_portfolio.create_trade(
                trade_id='long_2',
                enter_or_exit='enter',
                long_or_short='long',
                order_type='mkt',
                price=12.00
            )
            >>> new_market_trade
            >>> new_stop_trade = trading_robot_portfolio.create_trade(
                trade_id='long_3',
                enter_or_exit='enter',
                long_or_short='long',
                order_type='stop',
                price=2.00
            )
            >>> new_stop_trade
            >>> new_stop_limit_trade = trading_robot_portfolio.create_trade(
                trade_id='long_4',
                enter_or_exit='enter',
                long_or_short='long',
                order_type='stop-lmt',
                price=2.00,
                stop_limit_price=1.90
            )
            >>> new_stop_limit_trade
        Returns:
        ----
        Trade -- A pyrobot.Trade object with the specified template.
        """

        # Initalize a new trade object.
        trade = Trade()

        # Create a new trade.
        trade.new_trade(
            trade_id = trade_id,
            order_type = order_type,
            side = long_or_short,
            enter_or_exit = enter_or_exit,
            price = price,
            stop_limit_price = stop_limit_price
        )

        # Set the Client.
        trade.account = self.trading_account
        trade._webull_client = self.__webull_client__

        self.trades[trade_id] = trade

        return trade

    def delete_trade(self, index: int) -> None:
        """Deletes an exisiting trade from the `trades` collection.
        Arguments:
        ----
        index {int} -- The index of the order.
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
            )
            >>> new_trade = trading_robot_portfolio.create_trade(
                enter_or_exit='enter',
                long_or_short='long',
                order_type='mkt'
            )
            >>> trading_robot.delete_trade(index=1)
        """

        if index in self.trades:
            del self.trades[index]

    def create_stock_frame(self, data: List[dict]) -> StockFrame:
        """Generates a new StockFrame Object.
        Arguments:
        ----
        data {List[dict]} -- The data to add to the StockFrame object.
        Returns:
        ----
        StockFrame -- A multi-index pandas data frame built for trading.
        """

        # Create the Frame.
        self.stock_frame = StockFrame(data = data)

        return self.stock_frame

    def get_mfa(self, mfa: str):
        """Requests a multi-factor authentication code
        from Webull using the username or phone number.

        Returns:
        ----
        True if successfull, false otherwise
        """

        if self.__webull_client__ == None:
            raise Exception("Webull client is not initialized.")

        return self.__webull_client__.get_mfa(mfa)

    def get_security(self, username: str):
        """Requests a security question

        Returns:
        ----
        A listed dictionary with the question id, and question name
        """

        if self.__webull_client__ == None:
            raise Exception("Webull client is not initialized.")

        return self.__webull_client__.get_security(username)

    def unlock_trading(self, password: str):
        """Sends a request to unlock trading by sending
        a 6 digit password
        Usage:
        ----
        password -- The 6 digit password that unlocks money trading within
        the Webull client
        Returns:
        ----
        True if password was correct, False otherwise
        """

        if self.__webull_client__ == None:
            raise Exception("Webull client is not initialized.")

        return self.__webull_client__.get_trade_token(password)

    @property
    def pre_market_open(self) -> bool:
        """ Checks if pre-market is open.

        Uses the datetime module to create US Pre-Market hours in UTC time.

        Returns:
        ---
        bool - True if opened, false otherwise.
        """

        pre_market_startTime = datetime.utcnow().replace(
            hour = 8,
            minute = 00,
            second = 00
        ).timestamp()

        market_start_time = datetime.utcnow().replace(
            hour = 13,
            minute = 30,
            second = 00
        ).timestamp()

        current_time = datetime.utcnow().timestamp()

        if (current_time >= pre_market_startTime and current_time < market_start_time):
            return True
        
        return False

    @property
    def post_market_open(self) -> bool:
        """Checks if post-market is opened.

        Uses the datetime module to create US Post-Market hours in UTC time.

        Returns:
        ---
        bool - True if opened, False otherwise.
        """

        post_market_end_time = datetime.utcnow().replace(
            hour = 00,
            minute = 00,
            second = 00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour = 20,
            minute = 00,
            second = 00
        ).timestamp()

        current_time = datetime.utcnow().timestamp()

        if (current_time < post_market_end_time and current_time >= market_end_time):
            return True

        return False

    @property
    def market_open(self) -> bool:
        """Checks if the regular market is opened.

        Uses the datetime module to create US Regular Market hours in UTC time.

        Returns:
        ---
        bool - True if market is open, False otherwise.
        """

        market_start_time = datetime.utcnow().replace(
            hour = 13,
            minute = 30,
            second = 00
        ).timestamp()

        market_end_time = datetime.utcnow().replace(
            hour = 20,
            minute = 00,
            second = 00
        ).timestamp()

        current_time = datetime.utcnow().timestamp()

        if (market_end_time < current_time and market_start_time >= current_time):
            return True

        return False

    @property
    def get_login_status(self) -> Login:
        return self.LogType

    @property
    def set_login_status(self, logType: Login):
        self.LogType = logType

    @property
    def is_logged_in(self) -> bool:
        return self.__webull_client__.is_logged_in()

    @property
    def webull_client(self):
        return self.__webull_client__

    def grab_current_quotes(self) -> dict:
        """Grabs the current quotes for all positions in the portfolio.
        Makes a call to the TD Ameritrade Get Quotes endpoint with all
        the positions in the portfolio. If only one position exist it will
        return a single dicitionary, otherwise a nested dictionary.
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
            )
            >>> trading_robot_portfolio.add_position(
            symbol='MSFT',
            asset_type='equity'
            )
            >>> current_quote = trading_robot.grab_current_quotes()
            >>> current_quote
            {
                "MSFT": {
                    "assetType": "EQUITY",
                    "assetMainType": "EQUITY",
                    "cusip": "594918104",
                    ...
                    "regularMarketPercentChangeInDouble": 0,
                    "delayed": true
                }
            }
            >>> trading_robot = PyRobot(
            client_id=CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            credentials_path=CREDENTIALS_PATH
            )
            >>> trading_robot_portfolio.add_position(
            symbol='MSFT',
            asset_type='equity'
            )
            >>> trading_robot_portfolio.add_position(
            symbol='AAPL',
            asset_type='equity'
            )
            >>> current_quote = trading_robot.grab_current_quotes()
            >>> current_quote
            {
                "MSFT": {
                    "assetType": "EQUITY",
                    "assetMainType": "EQUITY",
                    "cusip": "594918104",
                    ...
                    "regularMarketPercentChangeInDouble": 0,
                    "delayed": False
                },
                "AAPL": {
                    "assetType": "EQUITY",
                    "assetMainType": "EQUITY",
                    "cusip": "037833100",
                    ...
                    "regularMarketPercentChangeInDouble": 0,
                    "delayed": False
                }
            }
        Returns:
        ----
        dict -- A dictionary containing all the quotes for each position.
        """

        # First grab all the symbols.
        symbols = self.portfolio.positions.keys()

        # Grab the quotes.
        quotes = self.session.get_quotes(instruments = list(symbols))

        return quotes

    def grab_historical_prices(self, start: datetime, end: datetime, bar_size: int = 1,
                               bar_type: str = 'minute', symbols: List[str] = None) -> List[dict]:
        """Grabs the historical prices for all the postions in a portfolio.
        Overview:
        ----
        Any of the historical price data returned will include extended hours
        price data by default.
        Arguments:
        ----
        start {datetime} -- Defines the start date for the historical prices.
        end {datetime} -- Defines the end date for the historical prices.
        Keyword Arguments:
        ----
        bar_size {int} -- Defines the size of each bar. (default: {1})
        bar_type {str} -- Defines the bar type, can be one of the following:
            `['minute', 'week', 'month', 'year']` (default: {'minute'})
        symbols {List[str]} -- A list of ticker symbols to pull. (default: None)
        Returns:
        ----
        {List[Dict]} -- The historical price candles.
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
                )
            >>> start_date = datetime.today()
            >>> end_date = start_date - timedelta(days=30)
            >>> historical_prices = trading_robot.grab_historical_prices(
                    start=end_date,
                    end=start_date,
                    bar_size=1,
                    bar_type='minute'
                )
        """

        self._bar_size = bar_size
        self._bar_type = bar_type

        start = str(milliseconds_since_epoch(dt_object = start))
        end = str(milliseconds_since_epoch(dt_object = end))

        new_prices = []

        if not symbols:
            symbols = self.portfolio.positions

        for symbol in symbols:

            historical_prices_response = self.session.get_price_history(
                symbol = symbol,
                period_type = 'day',
                start_date = start,
                end_date = end,
                frequency_type = bar_type,
                frequency = bar_size,
                extended_hours = True
            )

            self.historical_prices[symbol] = {}
            self.historical_prices[symbol]['candles'] = historical_prices_response['candles']

            for candle in historical_prices_response['candles']:

                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = symbol
                new_price_mini_dict['open'] = candle['open']
                new_price_mini_dict['close'] = candle['close']
                new_price_mini_dict['high'] = candle['high']
                new_price_mini_dict['low'] = candle['low']
                new_price_mini_dict['volume'] = candle['volume']
                new_price_mini_dict['datetime'] = candle['datetime']
                new_prices.append(new_price_mini_dict)

        self.historical_prices['aggregated'] = new_prices

        return self.historical_prices

    def get_latest_bar(self) -> List[dict]:
        """Returns the latest bar for each symbol in the portfolio.
        Returns:
        ---
        {List[dict]} -- A simplified quote list.
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
            )
            >>> latest_bars = trading_robot.get_latest_bar()
            >>> latest_bars
        """

        # Grab the info from the last quest.
        bar_size = self._bar_size
        bar_type = self._bar_type

        # Define the start and end date.
        end_date = datetime.today()
        start_date = end_date - timedelta(days=1)
        start = str(milliseconds_since_epoch(dt_object = start_date))
        end = str(milliseconds_since_epoch(dt_object = end_date))

        latest_prices = []

        # Loop through each symbol.
        for symbol in self.portfolio.positions:

            try:

                # Grab the request.
                historical_prices_response = self.session.get_price_history(
                    symbol = symbol,
                    period_type = 'day',
                    start_date = start,
                    end_date = end,
                    frequency_type = bar_type,
                    frequency = bar_size,
                    extended_hours = True
                )

            except:

                time_true.sleep(2)

                # Grab the request.
                historical_prices_response = self.session.get_price_history(
                    symbol = symbol,
                    period_type = 'day',
                    start_date = start,
                    end_date = end,
                    frequency_type = bar_type,
                    frequency = bar_size,
                    extended_hours = True
                )

            # parse the candles.
            for candle in historical_prices_response['candles'][-1:]:

                new_price_mini_dict = {}
                new_price_mini_dict['symbol'] = symbol
                new_price_mini_dict['open'] = candle['open']
                new_price_mini_dict['close'] = candle['close']
                new_price_mini_dict['high'] = candle['high']
                new_price_mini_dict['low'] = candle['low']
                new_price_mini_dict['volume'] = candle['volume']
                new_price_mini_dict['datetime'] = candle['datetime']
                latest_prices.append(new_price_mini_dict)

        return latest_prices

    def wait_till_next_bar(self, last_bar_timestamp: pd.DatetimeIndex) -> None:
        """Waits the number of seconds till the next bar is released.
        Arguments:
        ----
        last_bar_timestamp {pd.DatetimeIndex} -- The last bar's timestamp.
        """

        last_bar_time = last_bar_timestamp.to_pydatetime()[0].replace(tzinfo = timezone.utc)
        next_bar_time = last_bar_time + timedelta(seconds = 60)
        curr_bar_time = datetime.now(tz = timezone.utc)

        last_bar_timestamp = int(last_bar_time.timestamp())
        next_bar_timestamp = int(next_bar_time.timestamp())
        curr_bar_timestamp = int(curr_bar_time.timestamp())

        time_to_wait_now = next_bar_timestamp - curr_bar_timestamp

        if time_to_wait_now < 0:
            time_to_wait_now = 0

        print("=" * 80)
        print("Pausing for the next bar")
        print("-" * 80)
        print("Curr Time: {time_curr}".format(
            time_curr = curr_bar_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        print("Next Time: {time_next}".format(
            time_next = next_bar_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        print("Sleep Time: {seconds}".format(seconds = time_to_wait_now))
        print("-" * 80)
        print('')

        time_true.sleep(time_to_wait_now)

    def execute_signals(self, signals: List[pd.Series], trades_to_execute: dict) -> List[dict]:
        """Executes the specified trades for each signal.
        Arguments:
        ----
        signals {list} -- A pandas.Series object representing the buy signals and sell signals.
            Will check if series is empty before making any trades.
        Trades:
        ----
        trades_to_execute {dict} -- the trades you want to execute if signals are found.
        Returns:
        ----
        {List[dict]} -- Returns all order responses.
        Usage:
        ----
            >>> trades_dict = {
                    'MSFT': {
                        'trade_func': trading_robot.trades['long_msft'],
                        'trade_id': trading_robot.trades['long_msft'].trade_id
                    }
                }
            >>> signals = indicator_client.check_signals()
            >>> trading_robot.execute_signals(
                    signals=signals,
                    trades_to_execute=trades_dict
                )
        """
        
        # Define the Buy and sells.
        buys: pd.Series = signals['buys']
        sells: pd.Series = signals['sells']

        order_responses = []

        # If we have buys or sells continue.
        if not buys.empty:

            # Grab the buy Symbols.
            symbols_list = buys.index.get_level_values(0).to_list()

            # Loop through each symbol.
            for symbol in symbols_list:

                # Check to see if there is a Trade object.
                if symbol in trades_to_execute:

                    if self.portfolio.in_portfolio(symbol = symbol):
                        self.portfolio.set_ownership_status(
                            symbol = symbol,
                            ownership = True
                        )

                    # Set the Execution Flag.
                    trades_to_execute[symbol]['has_executed'] = True
                    trade_obj: Trade = trades_to_execute[symbol]['buy']['trade_func']

                    if not self.paper_trading:

                        # Execute the order.
                        order_response = self.execute_orders(
                            trade_obj = trade_obj
                        )

                        order_response = {
                            'order_id': order_response['order_id'],
                            'request_body': order_response['request_body'],
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

                    else:

                        order_response = {
                            'order_id': trade_obj._generate_order_id(),
                            'request_body': trade_obj.order,
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

        elif not sells.empty:

            # Grab the buy Symbols.
            symbols_list = sells.index.get_level_values(0).to_list()

            # Loop through each symbol.
            for symbol in symbols_list:

                # Check to see if there is a Trade object.
                if symbol in trades_to_execute:

                    # Set the Execution Flag.
                    trades_to_execute[symbol]['has_executed'] = True

                    if self.portfolio.in_portfolio(symbol=symbol):
                        self.portfolio.set_ownership_status(
                            symbol = symbol,
                            ownership = False
                        )

                    trade_obj: Trade = trades_to_execute[symbol]['sell']['trade_func']

                    if not self.paper_trading:

                        # Execute the order.
                        order_response = self.execute_orders(
                            trade_obj = trade_obj
                        )

                        order_response = {
                            'order_id': order_response['order_id'],
                            'request_body': order_response['request_body'],
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

                    else:

                        order_response = {
                            'order_id': trade_obj._generate_order_id(),
                            'request_body': trade_obj.order,
                            'timestamp': datetime.now().isoformat()
                        }

                        order_responses.append(order_response)

        # Save the response.
        self.save_orders(order_response_dict=order_responses)

        return order_responses

    def execute_orders(self, trade_obj: Trade) -> dict:
        """Executes a Trade Object.
        Overview:
        ----
        The `execute_orders` method will execute trades as they're signaled. When executed,
        the `Trade` object will have the order response saved to it, and the order response will
        be saved to a JSON file for further analysis.
        Arguments:
        ----
        trade_obj {Trade} -- A trade object with the `order` property filled out.
        Returns:
        ----
        {dict} -- An order response dicitonary.
        """

        # Execute the order.
        order_dict = self.session.place_order(
            account = self.trading_account,
            order = trade_obj.order
        )

        # Store the order.
        trade_obj._order_response = order_dict

        # Process the order response.
        trade_obj._process_order_response()

        return order_dict

    def get_positions(self, account_number: str = None, all_accounts: bool = False) -> List[Dict]:
        """Gets all the positions for a specified account number.
        Arguments:
        ----
        account_number (str, optional): The account number of the account you want
            to pull positions for. Defaults to None.
        all_accounts (bool, optional): If you want to return all the positions for every
            account then set to `True`. Defaults to False.
        Returns:
        ----
        List[Dict]: A list of Position objects.
        Usage:
        ----
            >>> trading_robot = PyRobot(
                client_id=CLIENT_ID,
                redirect_uri=REDIRECT_URI,
                credentials_path=CREDENTIALS_PATH
            )
            >>> trading_robot_positions = trading_robot.session.get_positions(
                account_number="<YOUR ACCOUNT NUMBER>"
            )
            >>> trading_robot_positions
            [
                {
                    'account_number': '111111111',
                    'asset_type': 'EQUITY',
                    'average_price': 0.00,
                    'current_day_profit_loss': -0.96,
                    'current_day_profit_loss_percentage': -5.64,
                    'cusip': '565849106',
                    'description': '',
                    'long_quantity': 3.0,
                    'market_value': 16.05,
                    'settled_long_quantity': 3.0,
                    'settled_short_quantity': 0.0,
                    'short_quantity': 0.0,
                    'sub_asset_type': '',
                    'symbol': 'MRO',
                    'type': ''
                },
                {
                    'account_number': '111111111',
                    'asset_type': 'EQUITY',
                    'average_price': 5.60667,
                    'current_day_profit_loss': -0.96,
                    'current_day_profit_loss_percentage': -5.64,
                    'cusip': '565849106',
                    'description': '',
                    'long_quantity': 3.0,
                    'market_value': 16.05,
                    'settled_long_quantity': 3.0,
                    'settled_short_quantity': 0.0,
                    'short_quantity': 0.0,
                    'sub_asset_type': '',
                    'symbol': 'MRO',
                    'type': ''
                }
            ]
        """

        if all_accounts:
            account = 'all'
        elif self.trading_account and account_number is None:
            account = self.trading_account
        else:
            account = account_number

        # Grab the positions.
        positions = self.session.get_accounts(
            account = account,
            fields = ['positions']
        )

        # Parse the positions.
        positions_parsed = self._parse_account_positions(
            positions_response = positions
        )

        return positions_parsed

    def _parse_account_positions(self, positions_response: Union[List, Dict]) -> List[Dict]:
        """Parses the response from the `get_positions` into a more simplified list.
        Arguments:
        ----
        positions_response {Union[List, Dict]} -- Either a list or a dictionary that represents a position.
        Returns:
        ----
        List[Dict] -- A more simplified list of positions.
        """

        positions_lists = []

        if isinstance(positions_response, dict):

            for account_type_key in positions_response:

                account_info = positions_response[account_type_key]

                account_id = account_info['accountId']
                positions = account_info['positions']

                for position in positions:
                    position_dict = {}
                    position_dict['account_number'] = account_id
                    position_dict['average_price'] = position['averagePrice']
                    position_dict['market_value'] = position['marketValue']
                    position_dict['current_day_profit_loss_percentage'] = position['currentDayProfitLossPercentage']
                    position_dict['current_day_profit_loss'] = position['currentDayProfitLoss']
                    position_dict['long_quantity'] = position['longQuantity']
                    position_dict['short_quantity'] = position['shortQuantity']
                    position_dict['settled_long_quantity'] = position['settledLongQuantity']
                    position_dict['settled_short_quantity'] = position['settledShortQuantity']

                    position_dict['symbol'] = position['instrument']['symbol']
                    position_dict['cusip'] = position['instrument']['cusip']
                    position_dict['asset_type'] = position['instrument']['assetType']
                    position_dict['sub_asset_type'] = position['instrument'].get(
                        'subAssetType', ""
                    )
                    position_dict['description'] = position['instrument'].get(
                        'description', ""
                    )
                    position_dict['type'] = position['instrument'].get(
                        'type', ""
                    )

                    positions_lists.append(position_dict)

        elif isinstance(positions_response, list):

            for account in positions_response:

                for account_type_key in account:

                    account_info = account[account_type_key]

                    account_id = account_info['accountId']
                    positions = account_info['positions']

                    for position in positions:
                        position_dict = {}
                        position_dict['account_number'] = account_id
                        position_dict['average_price'] = position['averagePrice']
                        position_dict['market_value'] = position['marketValue']
                        position_dict['current_day_profit_loss_percentage'] = position['currentDayProfitLossPercentage']
                        position_dict['current_day_profit_loss'] = position['currentDayProfitLoss']
                        position_dict['long_quantity'] = position['longQuantity']
                        position_dict['short_quantity'] = position['shortQuantity']
                        position_dict['settled_long_quantity'] = position['settledLongQuantity']
                        position_dict['settled_short_quantity'] = position['settledShortQuantity']

                        position_dict['symbol'] = position['instrument']['symbol']
                        position_dict['cusip'] = position['instrument']['cusip']
                        position_dict['asset_type'] = position['instrument']['assetType']
                        position_dict['sub_asset_type'] = position['instrument'].get(
                            'subAssetType', ""
                        )
                        position_dict['description'] = position['instrument'].get(
                            'description', ""
                        )
                        position_dict['type'] = position['instrument'].get(
                            'type', ""
                        )

                        positions_lists.append(position_dict)

        return positions_lists

    def get_current_orders(self):
        """Gets the current orders from Webull"""
        return self.__webull_client__.get_current_orders()

