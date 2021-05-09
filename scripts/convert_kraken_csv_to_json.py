#!/usr/bin/env python3
# File from https://gist.github.com/thisiscam/59ddae2ba2348bc8b2f4358e596fbb46
#
# Kraken data are available here: https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data
# 
"""
Convert CSV OHLCVT data from Kraken to JSON freqtrade format
"""
from typing import List, Dict

import os
import pathlib
import logging
import re

import tqdm
import pandas as pd

import ccxt

from freqtrade.exchange import timeframe_to_minutes
from freqtrade.data.history.idatahandler import get_datahandler
from freqtrade.constants import DEFAULT_DATAFRAME_COLUMNS

csv_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
#csv_columns = ['timestamp', 'price', 'amount']

logger = logging.getLogger(__name__)

def trades_to_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    timeframe_minutes = timeframe_to_minutes(timeframe)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
    df = df.set_index('timestamp')
    #df_new = df['price'].resample(f'{timeframe_minutes}min').ohlc()
    df_new['open'] = df['open'].resample(f'{timeframe_minutes}min')
    df_new['high'] = df['high'].resample(f'{timeframe_minutes}min')
    df_new['low'] = df['low'].resample(f'{timeframe_minutes}min')
    df_new['close'] = df['close'].resample(f'{timeframe_minutes}min')
    df_new['volume'] = df['volume'].resample(f'{timeframe_minutes}min').sum()
    df_new['date'] = df_new.index
    # Drop 0 volume rows
    df_new = df_new.dropna()
    return df_new.loc[:, DEFAULT_DATAFRAME_COLUMNS]


def convert_trades_to_ohlcv(pairs: Dict[str, pathlib.Path], timeframes: List[str],
                            datadir: pathlib.Path,
                            data_format_ohlcv: str = 'json') -> None:
    data_handler_ohlcv = get_datahandler(datadir, data_format=data_format_ohlcv)

    for pair, csv_file_path in tqdm.tqdm(pairs.items()):
        trades_df = pd.read_csv(csv_file_path, names=csv_columns, header=None)
        for timeframe in timeframes:
            try:
                ohlcv = trades_to_ohlcv(trades_df, timeframe)
                # Store ohlcv
                data_handler_ohlcv.ohlcv_store(pair, timeframe, data=ohlcv)
            except ValueError:
                logger.exception(f'Could not convert {pair} to OHLCV.')


def get_kraken_currency_alt_names():
    kraken = ccxt.kraken()
    currencies = kraken.fetchCurrencies()
    ret = {}
    for c in currencies.values():
        ret[c['id']] = c['name']
        ret[c['code']] = c['name']
        ret[c['name']] = c['name']
        ret[c['info']['altname']] = c['name']
    return ret


def get_kraken_pairs(kraken_csv_dir: pathlib.Path):
    """Fetch all the csv files in `kraken_csv_dir` and outputs currency pairs to a csv file."""
    currency_alt_names = get_kraken_currency_alt_names()
    currency_name_pattern = "|".join(map(re.escape, currency_alt_names.keys()))
    pair_pattern = rf"({currency_name_pattern})({currency_name_pattern}).csv"
    pair_pattern = re.compile(pair_pattern)
    pairs = {}
    for file in kraken_csv_dir.glob("*.csv"):
        match = pair_pattern.match(file.name)
        base_currency, to_currency = match.group(1), match.group(2)
        pairs[f"{currency_alt_names[base_currency]}/{currency_alt_names[to_currency]}"] = file
    return pairs


if __name__ == '__main__':
    kraken_csv_dir = pathlib.Path("~/Downloads/Kraken_Trading_History").expanduser()
    pairs = get_kraken_pairs(kraken_csv_dir)
    print(f"All pairs: {pairs.keys()}")
    convert_trades_to_ohlcv(
        pairs=pairs, timeframes=["1m", "5m"], 
        datadir=pathlib.Path("ohlcv"))
