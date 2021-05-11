# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from functools import reduce

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class BBRSINaiveStrategyWithHyperoptCode(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        # "30": 0.04,
        # "20": 0.06,
        "0": 0.08
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.3

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal ticker interval for the strategy.
    timeframe = '15m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
            'bb_upperband': {'color': 'green'},
            'bb_midband': {'color': 'orange'},
            'bb_lowerband': {'color': 'red'},
        },
        'subplots': {
            "RSI": {
                'rsi': {'color': 'yellow'},
            }
        }
    }

    buy_rsi = IntParameter(5, 50, default=25, space="buy")
    buy_rsi_enabled = CategoricalParameter([True, False], space="buy")
    buy_trigger = CategoricalParameter(['tr_bb_lower_1sd', 'tr_bb_lower_2sd', 'tr_bb_lower_3sd', 'tr_bb_lower_4sd'], space="buy")

    sell_rsi = IntParameter(30, 100, default=70, space="sell")
    sell_rsi_enabled = CategoricalParameter([True, False], space="sell")
    sell_trigger = CategoricalParameter(['sell_tr_bb_lower_1sd', 'sell_tr_bb_mid_1sd', 'sell_tr_bb_upper_1sd'], space="sell")


    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        # Bollinger bands
        bollinger_1sd = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=1)
        dataframe['bb_lowerband_1sd'] = bollinger_1sd['lower']
        dataframe['bb_middleband_1sd'] = bollinger_1sd['mid']
        dataframe['bb_upperband_1sd'] = bollinger_1sd['upper']

        bollinger_2sd = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband_2sd'] = bollinger_2sd['lower']
        dataframe['bb_middleband_2sd'] = bollinger_2sd['mid']
        dataframe['bb_upperband_2sd'] = bollinger_2sd['upper']

        bollinger_3sd = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=3)
        dataframe['bb_lowerband_3sd'] = bollinger_3sd['lower']
        dataframe['bb_middleband_3sd'] = bollinger_3sd['mid']
        dataframe['bb_upperband_3sd'] = bollinger_3sd['upper']

        bollinger_4sd = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=4)
        dataframe['bb_lowerband_4sd'] = bollinger_4sd['lower']
        dataframe['bb_middleband_4sd'] = bollinger_4sd['mid']
        dataframe['bb_upperband_4sd'] = bollinger_4sd['upper']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # GUARDS AND TRENDS
        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.buy_rsi.value)

        # TRIGGERS
        if self.buy_trigger.value == 'tr_bb_lower_1sd':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_1sd'])
        if self.buy_trigger.value == 'tr_bb_lower_2sd':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_2sd'])
        if self.buy_trigger.value == 'tr_bb_lower_3sd':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_3sd'])
        if self.buy_trigger.value == 'tr_bb_lower_4sd':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_4sd'])

        # Check that the candle had volume
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # GUARDS AND TRENDS
        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi.value)

            # TRIGGERS
        if self.sell_trigger.value == 'sell_tr_bb_lower_1sd':
            conditions.append(dataframe['close'] > dataframe['bb_lowerband_1sd'])
        if self.sell_trigger.value == 'sell_tr_bb_mid_1sd':
            conditions.append(dataframe['close'] > dataframe['bb_middleband_1sd'])
        if self.sell_trigger.value == 'sell_tr_bb_upper_1sd':
            conditions.append(dataframe['close'] > dataframe['bb_upperband_1sd'])

        # Check that the candle had volume
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1

        return dataframe
