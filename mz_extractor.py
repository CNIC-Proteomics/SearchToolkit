#!/usr/bin/python

# Module metadata variables
__author__ = ["Jose Rodriguez"]
__credits__ = ["Ricardo Magni", "Jose Rodriguez", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "1.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "jmrodriguezc@cnic.es"
__status__ = "Development"

# import modules
import os
import sys
import argparse
import logging
from argparse import RawTextHelpFormatter
import glob
import pandas as pd
import concurrent.futures
import itertools


#########################
# Import local packages #
#########################
sys.path.append(f"{os.path.dirname(__file__)}/libs")
import common
import PD
import MSFragger
import Comet
import Quant


###################
# Parse arguments #
###################

parser = argparse.ArgumentParser(
    description='Add the intensities into indentification file from the mzML reporting the ion isotopic distribution.',
    epilog='''
    Example:
        python mz_extractor.py \
            -i "tests/test1/modules/msfragger/*.tsv" \
            -z "tests/test1/modules/thermo_raw_parser/*.mzML" \
            -r "tests/test1/reporter_ion_isotopic.tsv" \
            -o "tests/test1/modules/mz_extractor"
    ''', formatter_class=RawTextHelpFormatter)
parser.add_argument('-w',  '--n_workers', type=int, default=2, help='Number of threads/n_workers (default: %(default)s)')
parser.add_argument('-i',  '--ident_files', required=True, help='Files with the identifications from search engine')
parser.add_argument('-z',  '--mzml_files', required=True, help='mzML files')
parser.add_argument('-r',  '--repor_ion', required=True, help='Table with the reporter ion isotopic distribution in TSV format')
parser.add_argument('-p',  '--ppm', default=10, help='Range of error in ppm')
parser.add_argument('-o',  '--outdir',  required=True, help='Output directory')
parser.add_argument('-vv', dest='verbose', action='store_true', help="Increase output verbosity")
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



###################
# Local functions #
###################
def read_infile(file):
    '''
    Read file
    '''
    # read input file
    try:
        df = pd.read_csv(file, sep="\t")
    except Exception as exc:
        sms = "Reading input file: {}".format(exc)
        logging.error(sms)
        sys.exit(sms)
    return df

def preprocessing_data(df, se):
    '''
    Processing the input files depending on search engine
    '''
    if se == "PD":
        df = PD.preprocessing_data(df)
    elif se == "Comet":
        df = Comet.preprocessing_data(df)
    elif se == "MSFragger":
        df = MSFragger.preprocessing_data(df)
    else:
        return df
    return df

def preprocessing(params):
    '''
    Extract the quantification
    '''
    # get params values
    spec_basename = params[0]
    ident_file = params[1]
    mzfile = params[2]
    ion_file = params[3]
    error_ppm = params[4]
    

    logging.info("reading the ident file")
    ddf = read_infile(ident_file)


    logging.info("extracting the search engines")
    se = common.select_search_engine(ddf)
    logging.debug(se)
    if not se:
        sms = "The search engines has not been recognized"
        logging.error(sms)
        sys.exit(sms)

    # pre-processing the df
    ddf = preprocessing_data(ddf, se)
    
    # add the Spectrum File column from the input file name
    if 'Spectrum_File' not in ddf.columns:
        ddf['Spectrum_File'] = spec_basename

    # create indata for the 
    indata = pd.DataFrame(data=[(spec_basename, mzfile, ion_file, error_ppm)],
                          columns=['spectrum_file', 'mzfile', 'quan_method', 'error_ppm'])
    
    return [ddf, indata]
    
def add_quantification(n_workers, ddf, indata):
    '''
    Extract the quantification
    '''
    
    # check if spectrum_file, mzfile and quan_method columns are fillin. Otherwise, the program does nothing.
    c = indata.columns.tolist()
    if 'spectrum_file' in c and 'mzfile' in c and 'quan_method' in c and not all(indata['spectrum_file'].str.isspace()) and not all(indata['mzfile'].str.isspace()) and not all(indata['quan_method'].str.isspace()):
        
        logging.info("compare spectrum_file/mzfile from the input_data and param_data")
        # convert groupby 'Spectrum_File' to dict for the input_data and param_data        
        ie_spec = dict(tuple(ddf.groupby("Spectrum_File")))
        in_spec = dict(tuple(indata.groupby("spectrum_file")))
        # check if all spectrum_files from inpu_data have a pair with  mzml coming from param_data        
        ie_spec_keys = list(ie_spec.keys())
        in_spec_keys = list(in_spec.keys())
        a = [ x for x in ie_spec_keys if not x in in_spec_keys ]
        if len(a) == 0:
            # for the 'spec_file' of input_data, get the mzMl of param_data
            pair_spec_ie_in = [ (k,v,in_spec[k]) for k,v in ie_spec.items() if k in in_spec]
    
            logging.info("prepare the params for each spectrum_file/mzfile pair")
            # one experiment can be multiple spectrum files
            with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:            
                params = executor.map( Quant.prepare_params, pair_spec_ie_in )
            params = [i for s in list(params) for i in s]
            # begin: for debugging in Spyder
            # params = Quant.prepare_params(pair_spec_ie_in[0])
            # end: for debugging in Spyder
    
            logging.info("extract the quantification")
            with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:            
                quant = executor.map( Quant.extract_quantification, params )
            quant = pd.concat(quant)
            # begin: for debugging in Spyder
            # quant = Quant.extract_quantification(params[0])
            # end: for debugging in Spyder
    
    
            logging.info("merge the quantification")
            with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:            
                ddf = executor.map( Quant.merge_quantification,
                                        list(ddf.groupby("Spectrum_File")),
                                        list(quant.groupby("Spectrum_File")) )
            ddf = pd.concat(ddf)
            # begin: for debugging in Spyder
            # ddf = Quant.merge_quantification( list(ddf.groupby("Spectrum_File"))[0], list(quant.groupby("Spectrum_File"))[0] )
            # end: for debugging in Spyder
        else:
            logging.error(f"The following Spectrum_Files have not mzML files: {a}")
            return None

    return ddf

def print_by_experiment(df, outdir):
    '''
    Print the output file by experiments
    '''
    # get the experiment names from the input tuple df=(exp,df)
    exp = df[0]
    # create workspace
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=False)
    # create temporal file
    name = os.path.splitext(os.path.basename(exp))[0]
    ext = os.path.splitext(os.path.basename(exp))[-1] or '.tsv'
    ofile = f"{outdir}/{name}{ext}.tmp"
    # basename = os.path.basename(exp)
    # ofile = os.path.join(outdir, f"{basename}.tmp")
    if os.path.isfile(ofile):
        os.remove(ofile)
    # print
    df[1].to_csv(ofile, index=False, sep="\t", lineterminator='\n')
    return ofile


    

def main(args):
    '''
    Main function
    '''
    
    logging.info("processing the identification files...")
    ifiles_ident = glob.glob(args.ident_files)
    # list of tuple (basename,filename,file)
    ifiles_ident = [(os.path.splitext(os.path.basename(f))[0],os.path.basename(f),f) for f in ifiles_ident]
    # sort the list of tuples based on the first element of each tuple
    ifiles_ident = sorted(ifiles_ident, key=lambda x: x[0])
    
    logging.info("processing the mzMLs...")
    ifiles_mzml = glob.glob(args.mzml_files)
    # list of tuple (basename,file)
    ifiles_mzml = [(os.path.splitext(os.path.basename(f))[0],f) for f in ifiles_mzml]
    # sort the list of tuples based on the first element of each tuple
    ifiles_mzml = sorted(ifiles_mzml, key=lambda x: x[0])

    
    logging.info("combining the identification files and mzMLs...")
    ifiles_ident_mzml = [ (x[0],x[2],y[1],args.repor_ion, args.ppm) for x,y in zip(ifiles_ident,ifiles_mzml) if x[0]==y[0] ]


    logging.info("preprocessing the parameters...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.n_workers) as executor:            
        pre = executor.map( preprocessing, ifiles_ident_mzml )
    pre = list(pre)
    # begin: for debugging in Spyder
    # quant = preprocessing(ifiles_ident_mzml[0])
    # end: for debugging in Spyder

    
    logging.info("extracting the quantification...")
    ddf = pd.concat([p[0] for p in pre], ignore_index=True)
    indata = pd.concat([p[1] for p in pre], ignore_index=True)
    ddf = add_quantification(args.n_workers, ddf, indata)


    logging.info("print the ID files by experiments")
    # get the outputdir. The filename by default
    outdir = args.outdir if args.outdir else os.path.join(os.path.dirname(ifile), script_name.lower())
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.n_workers) as executor:        
        tmpfiles = executor.map( print_by_experiment,
                                list(ddf.groupby("Spectrum_File")),
                                itertools.repeat(outdir) )
    [common.rename_tmpfile(f) for f in list(tmpfiles)] # rename tmp file deleting before the original file 
    # # begin: for debugging in Spyder
    # tmpfile = print_by_experiment(list(ddf.groupby("Spectrum_File"))[0], args.outdir)
    # common.rename_tmpfile(tmpfile)
    # # end: for debugging in Spyder
                



if __name__ == '__main__':    
    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')
