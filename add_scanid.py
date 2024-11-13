#!/usr/bin/python

# -*- coding: utf-8 -*-

# Module metadata variables
__author__ = "Andrea Laguillo Gómez"
__credits__ = ["Andrea Laguillo Gómez", "Ana Martínez del Val", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.3.0"
__maintainer__ = "Jose Rodriguez"
__email__ = "andrea.laguillo@cnic.es;jmrodriguezc@cnic.es"
__status__ = "Development"

# import modules
import os
import sys
import argparse
import logging
import pandas as pd
import re
from pathlib import Path

# Generate the Scan ID from the Spectrum File and the provided parameters
def add_scanId(df, ifile, ids):

    # add the file name without extension into 'Raw' column
    filename = 'Spectrum_File'
    if filename not in df.columns:
        df[filename] = '.'.join(os.path.basename(Path(ifile)).split(".")[:-1])

    # generate the scan id from the spectrum file and the given parameters
    scan_id = 'ScanID'
    if scan_id not in df.columns:
        # validate that all columns in 'ids' exist in the DataFrame
        missing_columns = [col for col in ids if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing columns in the input file: {', '.join(missing_columns)}")
            raise ValueError(f"Missing columns: {', '.join(missing_columns)}")
        # combine the specified columns to create the ScanID
        df[scan_id] = df[[filename]+ids].astype(str).agg('-'.join, axis=1)

    return df

def main(args):
    '''
    Main function
    '''
    # preparing the given parameters
    logging.info('Preparing parameters')
    # getting input parameters
    ifile = args.infile
    # get the output file
    # if output directory is not defined, get the folder from given file
    # get the base name of the input file
    # construct output file path with "_XXX" appended to the filename
    # log files

    # outdir = args.outdir if args.outdir else os.path.dirname(ifile)
    # basename = os.path.splitext(os.path.basename(ifile))[0]
    # extension = os.path.splitext(os.path.basename(ifile))[1]
    # ofile = os.path.join(outdir, f"{basename}_ScanID{extension}")

    outdir = args.outdir if args.outdir else os.path.join(os.path.dirname(ifile), script_name.lower())
    os.makedirs(outdir, exist_ok=False)
    basename = os.path.basename(ifile)
    ofile = os.path.join(outdir, basename)

    # get the list of column names that compose the ScanID
    ids = re.split(r'\s*,\s*', args.ids)


    # obtain the first line
    logging.info('Giving the input file ' + str(ifile))
    with open(ifile) as f:
        first_line = f.readline().strip().split('\t')
    
    # read the data depending on the type of search engine
    search_engine_name = 'msfragger'
    if 'CometVersion' in first_line[0]:
        logging.info('Reading the "comet" data file...')
        df = pd.read_csv(ifile, sep='\t', skiprows=1, float_precision='high', low_memory=False, index_col=False)
        search_engine_name = 'comet'
    else:
        logging.info('Reading the "msfragger" data file...')
        df = pd.read_csv(ifile, sep='\t', float_precision='high', low_memory=False, index_col=False)
        search_engine_name = 'msfragger'
    logging.info(f"File {ifile} loaded successfully with {len(df)} rows.")


    # if applicable, generate the Scan ID from the Spectrum File and the provided parameters
    logging.info('Generating ScanID')
    df = add_scanId(df, ifile, ids)


    # write file
    logging.info(f"Output file will be saved as: {ofile}")
    df = df.reset_index(drop=True)
    df.to_csv(ofile, index=False, sep='\t', encoding='utf-8')
        

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(
        description='''\
        add_scanid: A tool for adapting search engine results.

        This tool processes results from both the Comet-PTM and MSFragger search engines.
        In both cases, a 'Spectrum_File' column is added based on the input file name.
        Additionally, a column with the Scan ID is created based on the 'Spectrum_File' 
        and the provided parameters.
        ''',
        epilog='''\
        Example:
            python add_scanid.py -i path/to/input/file -o path/to/output/directory

        For further assistance, please refer to the documentation or contact support.
        '''
    )
    parser.add_argument('-i', '--infile', required=True, help='Path to the input file')
    parser.add_argument('-d', '--ids', required=True, help='Column names combined with the filename to create the Scan ID')
    parser.add_argument('-o', '--outdir', help='Path to the output directory')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # get the name of script
    script_name = os.path.splitext( os.path.basename(__file__) )[0].upper()

    # logging debug level. By default, info level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format=script_name+' - '+str(os.getpid())+' - %(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.INFO,
                            format=script_name+' - '+str(os.getpid())+' - %(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')

    # start main function
    logging.info('start script: '+'{0}'.format(' '.join([x for x in sys.argv])))
    main(args)
    logging.info('end script')
        