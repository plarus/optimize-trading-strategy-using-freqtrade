#!/usr/bin/env python3
#
# Extract hyperopt result and put it in a CSV file.
#
# usage: extract_hyperopt_result.py [-h] [-i INPUT] [-o OUTPUT]

import re
import json
import csv
import argparse
import sys
import os
import select

def extract(input_file):
    pattern = "^.* +([0-9]+)\/([0-9]+): +([0-9]+).+\. +([0-9]+)\/([0-9]+)\/([0-9]+) +.+(-?[0-9]+\.[0-9]+)%\. +Median.+(-?[0-9]+\.[0-9]+)%\. +.+ +(-?[0-9]+\.[0-9]+) +([A-Z]+) +\( +(-?[0-9]+\.[0-9]+)Σ%\)\. +.+ +([0-9]+\.?[0-9]*) +.+: +(-?[0-9]+\.[0-9]+)"
    columns = ['all','epoch','nb_epoch','trades','wins','draws','losses','avg_profit','median_profit','total_profit', 'profit_unit', 'profit_percent','avg_duration','objective']

    # Read hyperopt result
    for line in input_file:
        if re.search("Wins/Draws/Losses", line):
            result = re.match(pattern, line)
            if result != None: 
                dict_data = {col_name:result.group(n) for n, col_name in enumerate(columns) }
                
                # Remove 1st column
                dict_data.pop('all')

        # Get the params part in json format
        elif re.search("{\"params\"", line):
            json_param = json.loads(line)
            break

    if 'dict_data' in locals() and 'json_param' in locals() :
        dict_data.update(json_param['params'])
        
        return dict_data
    else:
       sys.exit('Expected input not found...') 

def convert(dict_data, csv_file_name):

    if not os.path.isfile(csv_file_name):
        # Create file with header
        with open(csv_file_name, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=dict_data.keys())
            writer.writeheader()
            writer.writerow(dict_data)
    else:
        # Add a line
        with open(csv_file_name, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=dict_data.keys())
            writer.writerow(dict_data)

def main(argv):
    parser = argparse.ArgumentParser(description='Extract hyperopt result and put it in a CSV file.')
    parser.add_argument('-i', '--input', help='Input file (Default: stdin)')
    parser.add_argument('-o', '--output', default='./hyperopt_res.csv', help='Output file')
    parser.add_argument('-s', '--strategie', help='Used strategie')
    parser.add_argument('-l', '--lossFunction', help='Used loss function')
    parser.add_argument('-t', '--timeframe', help='Used timeframe')

    args = parser.parse_args()

    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, 'r') as input_file:
                dict_data = extract(input_file)
        else:
            sys.exit('\"' + args.input + '\" is not a valid file...')
    else:
        # Check if stdin datas are available
        if select.select([sys.stdin,],[],[],0.0)[0]:
            dict_data = extract(sys.stdin)
        else:
            sys.exit("Not data from stdin...")

    if args.strategie:
        dict_data['strategie'] =  args.strategie

    if args.lossFunction:
        dict_data['lossFunction'] =  args.lossFunction

    if args.timeframe:
        dict_data['timeframe'] =  args.timeframe

    convert(dict_data, args.output)

if __name__ == "__main__":
    main(sys.argv[1:])

