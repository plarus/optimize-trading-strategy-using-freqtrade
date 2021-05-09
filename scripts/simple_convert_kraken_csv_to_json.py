#!/usr/bin/env python3
#
# Kraken data are available here: https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data
#

"""
Convert CSV OHLCVT data from Kraken to JSON freqtrade format

Usage 1: simple_convert_kraken_csv_to_json.py "INPUT_CSV" ["OUTPUT_JSON"]
Usage 2: simple_convert_kraken_csv_to_json.py "INPUT_DIR"
"""

import sys
import os
import pandas as pd

CSV_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']
FIAT_NAME = 'EUR'

def convert_name(filename, fiat_name):
    crypto_name = filename.split(fiat_name)[0]
    timeframe = int(filename.split('_')[1])
    if timeframe <= 30:
        unit = 'm'
    elif timeframe <= 720: # 12h
        timeframe = timeframe / 60
        unit = 'h'
    else:
        timeframe = timeframe / 60 / 24
        unit = 'd'

    return crypto_name + '_' + fiat_name + '-' + str(timeframe) + unit

def convert_file(csv_file_path, json_file_path):
    trades_df = pd.read_csv(csv_file_path, names=CSV_COLUMNS, header=None)

    trades_df['date'] = pd.to_datetime(trades_df['timestamp'], unit='s', utc=True)

    # Drop 0 volume rows
    trades_df = trades_df.dropna()

    # Export to JSON freqtrade format
    trades_df.loc[:, ['date', 'open', 'high', 'low', 'close', 'volume']].to_json(json_file_path, orient="values")

def main(argv):

    # If directory => Convert all files
    if os.path.isdir(argv[0]):
        directory = argv[0]
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                csv_file_path = os.path.join(directory, filename)
                json_file = convert_name(filename.rsplit('.', 1)[0], FIAT_NAME) + '.json'
                json_file_path = os.path.join(directory, json_file)
                convert_file(csv_file_path, json_file_path)
    else:
        csv_file_path = argv[0]

        try:
            argv[1]
        except IndexError:
            csv_file = os.path.basename(csv_file_path)
            directory = os.path.dirname(csv_file_path)
            json_file = convert_name(csv_file.rsplit('.', 1)[0], FIAT_name) + '.json'
            json_file_path = os.path.join(directory, json_file)
        else:
            json_file_path = argv[1]

        convert_file(csv_file_path, json_file_path)

if __name__ == "__main__":
   main(sys.argv[1:])

