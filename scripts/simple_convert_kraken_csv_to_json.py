#!/usr/bin/env python3
#
# Kraken data are available here: https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data
#

"""
Convert CSV OHLCVT data from Kraken to JSON freqtrade format

usage: simple_convert_kraken_csv_to_json.py [-h] [-f FIAT] [-o OUTPUT] [INPUT_PATH]

"""

import sys
import os
import pandas as pd
import re
import argparse

CSV_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trades']

def convert_name(input_path, fiat_name, output_dir):

    filename = os.path.basename(input_path).rsplit('.', 1)[0]

    crypto_name = filename.split(fiat_name)[0]
    timeframe = int(filename.split('_')[1])
    if timeframe < 60:
        unit = 'm'
    elif timeframe < 1440: # 24h
        timeframe = int(timeframe / 60)
        unit = 'h'
    else:
        timeframe = int(timeframe / 60 / 24)
        unit = 'd'

    json_file = crypto_name + '_' + fiat_name + '-' + str(timeframe) + unit + '.json'

    return os.path.join(output_dir, json_file)


def convert_file(csv_file_path, json_file_path):
    trades_df = pd.read_csv(csv_file_path, names=CSV_COLUMNS, header=None)

    trades_df['date'] = pd.to_datetime(trades_df['timestamp'], unit='s', utc=True)

    # Drop 0 volume rows
    trades_df = trades_df.dropna()

    # Export to JSON freqtrade format
    trades_df.loc[:, ['date', 'open', 'high', 'low', 'close', 'volume']].to_json(json_file_path, orient="values")


def main(argv):
    parser = argparse.ArgumentParser(description='Convert CSV OHLCVT data from Kraken to JSON freqtrade format.')
    parser.add_argument('input_path', metavar='INPUT_PATH', type=str, nargs='?', default='.', help='Path to the input file or directory (Default: current directory)')
    parser.add_argument('-f', '--fiat', default='EUR', help='Convert files with the specified FIAT (Default: EUR)')
    parser.add_argument('-o', '--output', help='Path to the output file or directory')

    args = parser.parse_args()
    
    # If directory => Convert all files
    if os.path.isdir(args.input_path):
        if args.output:
            output_dir = args.output
        else:
            output_dir = args.input_path

        for csv_file in os.listdir(args.input_path):
            # Convert only files with the expected name
            if re.findall('.*' + args.fiat + '_[0-9]*\.csv', csv_file):
                json_file_path = convert_name(csv_file, args.fiat, output_dir)
                convert_file(os.path.join(args.input_path, csv_file), json_file_path)
    else:
        # Manage output file name
        if args.output:
            if os.path.isdir(args.output):
                json_file_path = convert_name(args.input_path, args.fiat, args.output)
            else:
                json_file_path = args.output
        else:
            json_file_path = convert_name(args.input_path, args.fiat, os.path.dirname(args.input_path))

        convert_file(args.input_path, json_file_path)

if __name__ == "__main__":
    main(sys.argv[1:])

