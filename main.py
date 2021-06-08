import datetime
import getopt, sys

import log
from arn import Arn
from compare_arn import compare_strict_arn, compare_line_arn, compare_loop_arn


def usage():
    help_text = """This script is used to compare sequence of nucleotides
        
        This script accept parameters of this list. 
        
        --help (shortcut: -h)
            Show the way how use the script
        --sequence1
            First Sequence to be compare.
            Example = --sequence1=UCGA
            Default value is : UCGUACCGUGAGUAAUAAUGCGB
        --sequence2
            Second Sequence to be compare. 
            Example = --sequence1=UCGA
            Default value is : UAACACUGUCUGGUAACGAUGU
        --percent
            Variable of percentage of accepted comparison. 
            Only used for the line comparison
            Example = --percent=50
            Default value is : 30
        --decalSeq1
            If Not Provided : it will add space to sequence 1.
            If yes: it will add space to sequence 2.
            Example = --decalSeq1
        --verbose
            If provided ; it will print in standard output logs.
            If not : it will not print logs.
            Example = --verbose
        --output
            Specify the file where the file of result will be create.
            Example = --output=/tmp/resultFile.txt
        --nbProcess
            Specify the number of process used for treatment which need processing long time.
            Default : 1
            Example = --nbProcess=2
"""
    print(help_text)


if __name__ == "__main__":
    # execute only if run as a script
    error_percent = 30
    sequence_1 = "UCGUACCGUGAGUAAUAAUGCGB"
    sequence_2 = "UAACACUGUCUGGUAACGAUGQ"
    # jf true so it will add space before sequence 2
    # If False so it will add space before sequence 1
    add_space_sequence1 = True
    filename_output = ""
    is_verbose = False
    nb_process = 1

    try:
        opts, argv = getopt.getopt(
            sys.argv[1:],
            "h",
            ['help', 'sequence1=', 'sequence2=', 'percent=', 'output=', 'decalSeq1', 'verbose', 'nbProcess']
        )
    except getopt.GetoptError as err:
        usage()
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    for k, v in opts:
        if k == '-h' or k == '--help':
            usage()
            sys.exit(0)
        if k == '--sequence1':
            sequence_1 = v
        if k == '--sequence2':
            sequence_2 = v
        if k == '--percent':
            error_percent = v
        if k == '--output':
            filename_output = v
        if k == '--decalSeq1':
            add_space_sequence1 = False
        if k == '--verbose':
            is_verbose = True
        if k == '--nbProcess':
            nb_process = v

    logger = log.Log(None, is_verbose, filename_output)
    arn1 = Arn(sequence_1)
    arn2 = Arn(sequence_2)

    dateDebut = datetime.datetime.now()

    # logger.debug("-------------------------------------")
    # logger.debug("Check sequences Start.")
    # compare_strict_arn(arn1, arn2, logger)
    # logger.debug("Check sequences End.")
    # logger.debug("-------------------------------------")

    # logger.debug("-------------------------------------")
    # logger.debug("Check sequences with linear method Start.")
    # compare_line_arn(arn1, arn2, logger, add_space_sequence1, error_percent)
    # logger.debug("Check sequences with linear method End.")
    # logger.debug("-------------------------------------")

    logger.debug("-------------------------------------")
    logger.debug("Check sequences Loop Method Start.")
    compare_loop_arn(arn1, arn2, logger, error_percent, nb_process)
    logger.debug("Check sequences Loop Method End.")
    logger.debug("-------------------------------------")


    print(dateDebut)
    print(datetime.datetime.now())

