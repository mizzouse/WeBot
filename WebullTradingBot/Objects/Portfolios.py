from pandas import DataFrame
from typing import Tuple
from typing import List
from typing import Optional

from Objects.StockFrame import StockFrame
from webull import webull
from webull import paper_webull

class Portfolio():
    def __init__(self, account_number: Optional[str] = None) -> None:
        self.positions = {}
        self.positions_count = 0
        self.market_value = 0.0
        self.profit_loss = 0.0
        self.risk_tolerance = 0.0

        self.account_number = account_number
        self._stock_frame: StockFrame = None
        self._stock_frame_daily: StockFrame = None
        self.__webull_client__: object = None

    def add_position(self, symbol: str, asset_type: str, purchase_date: Optional[str], quantity: int = 0, purchase_price: float = 0.0) -> dict:
        """Adds a single new position to the the portfolio.
        Arguments:
        ----
        symbol {str} -- The Symbol of the Financial Instrument. Example: 'AAPL' or '/ES'
        asset_type {str} -- The type of the financial instrument to be added. For example,
            'equity', 'forex', 'option', 'futures'
        Keyword Arguments:
        ----
        quantity {int} -- The number of shares or contracts you own. (default: {0})
        purchase_price {float} -- The price at which the position was purchased. (default: {0.00})
        purchase_date {str} -- The date which the asset was purchased. Must be ISO Format "YYYY-MM-DD"
            For example, "2020-04-01" (default: {None})
        Returns:
        ----
        {dict} -- A dictionary object that represents a position in the portfolio.
        Usage:
        ----
            >>> portfolio = Portfolio()
            >>> new_position = Portfolio.add_position(symbol='MSFT', 
                    asset_type='equity', 
                    quantity=2, 
                    purchase_price=4.00,
                    purchase_date="2020-01-31"
                )
            >>> new_position
            {
                'asset_type': 'equity', 
                'quantity': 2, 
                'purchase_price': 4.00,
                'symbol': 'MSFT',
                'purchase_date': '2020-01-31'
            }
        """
        self.positions[symbol] = {}
        self.positions[symbol]['symbol'] = symbol
        self.positions[symbol]['quantity'] = quantity
        self.positions[symbol]['purchase_price'] = purchase_price
        self.positions[symbol]['purchase_date'] = purchase_date
        self.positions[symbol]['asset_type'] = asset_type

        return self.positions

    def add_positions(self, positions: List[dict]) -> dict:
        """Add Multiple positions to the portfolio at once.
        This method will take an iterable containing the values
        normally passed through in the `add_position` endpoint and
        then adds each position to the portfolio.
        Arguments:
        ----
        positions {list[dict]} -- Multiple positions with the required arguments to be added.
        Returns:
        ----
        {dict} -- The current positions in the portfolio.
        Usage:
        ----
            >>> # Define mutliple positions to add.
            >>> multi_position = [
                {
                    'asset_type': 'equity',
                    'quantity': 2,
                    'purchase_price': 4.00,
                    'symbol': 'TSLA',
                    'purchase_date': '2020-01-31'
                },
                {
                    'asset_type': 'equity',
                    'quantity': 2,0
                    'purchase_price': 4.00,
                    'symbol': 'SQ',
                    'purchase_date': '2020-01-31'
                }
            ]
            >>> new_positions = trading_robot.portfolio.add_positions(positions=multi_position)
            {
                'SQ': {
                    'asset_type': 'equity',
                    'purchase_date': '2020-01-31',
                    'purchase_price': 4.00,
                    'quantity': 2,
                    'symbol': 'SQ'
                },
                'TSLA': {
                    'asset_type': 'equity',
                    'purchase_date': '2020-01-31',
                    'purchase_price': 4.00,
                    'quantity': 2,
                    'symbol': 'TSLA'
                }
            }
        """
        if isinstance(positions, list):

            # Loop through each position.
            for position in positions:

                # Add the position.
                self.add_position(
                    symbol = position['symbol'],
                    asset_type = position['asset_type'],
                    quantity = position.get('quantity', 0),
                    purchase_price = position.get('purchase_price', 0.0),
                    purchase_date = position.get('purchase_date', None)
                )

            return self.positions
        else:
            raise TypeError("Positions must be a list of dictionaries.")

    def remove_position(self, symbol: str) -> Tuple[bool, str]:
        """Deletes a single position from the portfolio.
        Arguments:
        ----
        symbol {str} -- The symbol of the instrument to be deleted. Example: 'AAPL' or '/ES'
        Returns:
        ----
        {Tuple[bool, str]} -- Returns `True` if successfully deleted, `False` otherwise 
            along with a message.
        Usage:
        ----
            >>> portfolio = Portfolio()
            >>> new_position = Portfolio.add_position(
                    symbol='MSFT', 
                    asset_type='equity', 
                    quantity=2, 
                    purchase_price=4.00,
                    purchase_date="2020-01-31"
                )
            >>> delete_status = Portfolio.delete_position(symbol='MSFT')
            >>> delete_status
            (True, 'MSFT was successfully removed.')
            >>> delete_status = Portfolio.delete_position(symbol='AAPL')
            >>> delete_status
            (False, 'AAPL did not exist in the porfolio.')
        """

        if symbol in self.positions:
            del self.positions[symbol]
            return (True, "{symbol} was successfully removed.".format(symbol = symbol))
        else:
            return (False, "{symbol} did not exist in the porfolio.".format(symbol = symbol))

    def in_portfolio(self, symbol: str) -> bool:
        """checks if the symbol is in the portfolio.
        Arguments:
        ----
        symbol {str} -- The symbol of the instrument to be deleted. Example: 'AAPL' or '/ES'
        Returns:
        ----
        bool -- `True` if the position is in the portfolio, `False` otherwise.
        Usage:
        ----
            >>> portfolio = Portfolio()
            >>> new_position = Portfolio.add_position(
                symbol='MSFT', 
                asset_type='equity'
            )
            >>> in_position_flag = Portfolio.in_portfolio(symbol='MSFT')
            >>> in_position_flag
                True
        """

        if symbol in self.positions:
            return True
        else:
            return False

    def total_allocation(self) -> dict:
        """Returns a summary of the portfolio by asset allocation."""

        total_allocation = {
            'stocks': [],
            'fixed_income': [],
            'options': [],
            'futures': [],
            'forex': []
        }

        if len(self.positions.keys()) > 0:
            for symbol in self.positions:
                total_allocation[self.positions[symbol]['asset_type']].append(self.positions[symbol])

    def is_profitable(self, symbol: str, current_price: float) -> bool:
        """Specifies whether a position is profitable.
        Arguments:
        ----
        symbol {str} -- The symbol of the instrument, to check profitability.
        current_price {float} -- The current trading price of the instrument.
        Returns:
        ----
        {bool} -- Specifies whether the position is profitable or flat `True` or not
            profitable `False`.
        Raises:
        ----
        KeyError: If the Symbol does not exist it will return a key error.
        Usage:
        ----
            >>> portfolio = Portfolio()
            >>> new_position = Portfolio.add_position(
                symbol='MSFT', 
                asset_type='equity',
                purchase_price=4.00,
                purchase_date="2020-01-31"
            )
            >>> is_profitable_flag = Portfolio.is_profitable(
                symbol='MSFT',
                current_price=7.00
            )
            >>> is_profitable_flag
            True
        """

        # Grab the purchase price, if it exists.
        if self.in_portfolio(symbol = symbol):
            purchase_price = self.positions[symbol]['purchase_price']
        else:
            raise KeyError("The Symbol you tried to request does not exist.")

        if (purchase_price <= current_price):
            return True
        elif (purchase_price > current_price):
            return False

    @property
    def stock_frame(self) -> StockFrame:
        """Gets the StockFrame object for the Portfolio
        Returns:
        ----
        {StockFrame} -- A StockFrame object with symbol groups, and rolling windows.
        """

        return self._stock_frame

    @stock_frame.setter
    def stock_frame(self, stock_frame: StockFrame) -> None:
        """Sets the StockFrame object for the Portfolio
        Arguments:
        ----
        stock_frame {StockFrame} -- A StockFrame object with symbol groups, and rolling windows.
        """

        self._stock_frame = stock_frame

    @property
    def webull_client(self):
        """Gets the webull object for the Portfolio
        Returns:
        ----
        {webull} -- An authenticated session with the Webull API.
        """

        return self.__webull_client__

    @webull_client.setter
    def webull_client(self, webull_client) -> None:
        """Sets the webull object for the Portfolio
        Arguments:
        ----
        webull_client {webull} -- An authenticated session with the Webull API.
        """

        self.__webull_client__ = webull_client