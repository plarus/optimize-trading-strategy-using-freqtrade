#!/usr/bin/env python3
# Extract all pickle hyperopt result in a CSV file

import re
import os
import sys
import argparse

def hyperopt_show(pickle_file):
    cmd = "sudo docker-compose run --rm freqtrade hyperopt-show --print-json --best --hyperopt-filename " + pickle_file + " > tmp.log"
    os.system(cmd)
    cmd = "./extract_hyperopt_result.py -i tmp.log"
    os.system(cmd)

def main(argv):
    parser = argparse.ArgumentParser(description='Extract all hyperopt results from pickle files.')
    parser.add_argument('input_path', metavar='INPUT_PATH', type=str, nargs='?', default='.', help='Path to the input file or directory (Default: current directory)')

    args = parser.parse_args()
    
    # If directory => Manage all files
    if os.path.isdir(args.input_path):
        for pickle_file in os.listdir(args.input_path):
            if re.findall('.*\.pickle', pickle_file):
                hyperopt_show(pickle_file)
    else:
        hyperopt_show(args.input_path)

if __name__ == "__main__":
    main(sys.argv[1:])

