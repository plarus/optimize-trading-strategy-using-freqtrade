#!/usr/bin/env python3
#

import re
import json
import csv
import argparse
import sys
import os
import select

def convert(input_file, csv_file_name):
    pattern = "^\* +([0-9]+)\/([0-9]+): +([0-9]+).+\. +([0-9]+)\/([0-9]+)\/([0-9]+) +.+(-?[0-9]+\.[0-9]+)%\. +Median.+(-?[0-9]+\.[0-9]+)%\. +.+ +(-?[0-9]+\.[0-9]+) +([A-Z]+) +\( +(-?[0-9]+\.[0-9]+)Σ%\)\. +.+ +([0-9]+\.?[0-9]*) +.+: +(-?[0-9]+\.[0-9]+)"
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

        #list_params.append(dict_data)

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
    else:
       sys.exit('Expected input not found...') 

def main(argv):
    parser = argparse.ArgumentParser(description='Extract hyperopt result and put it in a CSV file.')
    parser.add_argument('-i', '--input', help='Input file (Default: stdin)')
    parser.add_argument('-o', '--output', default='./hyperopt_res.csv', help='Output file')
    
    args = parser.parse_args()

    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, 'r') as input_file:
                convert(input_file, args.output)
        else:
            sys.exit('\"' + args.input + '\" is not a valid file...')
    else:
        # Check if stdin datas are available
        if select.select([sys.stdin,],[],[],0.0)[0]:
            convert(sys.stdin, args.output)
        else:
            sys.exit('Not data from stdin...')

if __name__ == "__main__":
    main(sys.argv[1:])
