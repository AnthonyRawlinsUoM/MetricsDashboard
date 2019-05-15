#! /usr/bin/env python3

import argparse
import os

import progressbar

from redis import Redis
from pathlib import Path

from apps.BioDiversity import BioDiversity
from apps.Carbon import Carbon
from apps.Experiential import Experiential
from apps.Hydrology import Hydrology
from apps.ImplementationCost import ImplementationCost
from apps.MetricAdaptor import MetricAdaptor
from apps.PeopleHouses import PeopleHouses
from apps.Infrastructure import Infrastructure
from apps.Recreational import Recreational
from apps.RegionalEconomy import RegionalEconomy

from apps.util import Util

import logging
# Some application level constants
PP_OUTPUT_PATH = "post_processing_output"
EXTRACTION_LOG = "extractions.log"
SAVING = True

###############################################################################
APP_NAME = 'Extractor'
APP_VERSION = '1.0.0'
###############################################################################

logging.basicConfig(filename=EXTRACTION_LOG, level=logging.DEBUG)
logger = logging.getLogger(name=APP_NAME + ' v' + APP_VERSION)


def main(args):
    Util.clear()
    Util.program_header()

    # Path and Permissions checking
    if not Path(args.path).exists():
        raise Exception("The root path does not seem to exist.")

    if not Path(args.path).is_dir():
        raise Exception("The root path seems to not be a folder.")

    if not Util.readable(args.path):
        raise Exception("The root path is not readable.")

    # Check existence of PB levels subfolders

    sorted_pb_list = Util.get_pb_levels(args.path, args.name)

    # print('Found the following FROST outputs:')
    # [print('PB level: %s' % (i.split('_')[-1])) for i in sorted_pb_list]

    # menu = setup()
    # menu.show()

    if not args.lvls:
        pb_levels = []
    else:
        pb_levels = list(map(int, args.lvls.split(',')))

    pb_selection_complete = False

    while len(pb_levels) == 0 or not pb_selection_complete:
        Util.clear()
        Util.program_header()
        print('We will parse the following FROST outputs:')
        print()
        for i in sorted_pb_list:
            lvl = int(i.split('_')[-1])
            if lvl in pb_levels:
                used = "X"
            else:
                used = " "
            print('[%s] PB level:%3d' % (used, lvl))

        # Get user input

        print()
        Util.rule()
        inbuf = input('Enter PB levels to extract [Enter to continue]: ')
        # Check for empty Input
        if inbuf == "":
            pb_selection_complete = True
        else:
            # validate input
            try:
                if inbuf in sorted_pb_list:
                    pb_levels.append(int(inbuf))
                else:
                    print("Not a valid option, try again.")
            except ValueError as e:
                print(e)

    redis = None
    redis_configured = False
    try:
        redis = Redis(host=os.environ['REDIS_HOST'], port=6379)
    except KeyError as e:
        print(e)
    try:
        while not redis_configured:
            Util.clear()
            Util.program_header()
            print("Enter the HOST ADDRESS for the REDIS server:")
            Util.rule()
            REDIS_HOST = "localhost"
            inbuf = input("[Default (%s)]: " % REDIS_HOST)
            if inbuf != "":
                REDIS_HOST = inbuf
            # Test Connection

            redis = Redis(host=REDIS_HOST, port=6379)
            if redis.set('test', 1234):
                rinfo = redis.info()
                Util.clear()
                Util.program_header()
                print("Found %s %s REDIS Server v%s on port %s" % (rinfo['redis_mode'],
                                                                   rinfo['role'],
                                                                   rinfo['redis_version'],
                                                                   rinfo['tcp_port']
                                                                   ))
                print(">> Connection Succeeded.")
                print(">> Extracted Data will be stored on '%s'" % (REDIS_HOST))
                redis_configured = True
            else:
                print(">> Connection Test Failed!")

    except ConnectionError as e:
        print(e)

    schemas = [
        MetricAdaptor(BioDiversity(args.path, args.name, redis),
                      extract='load', question='question'),
        MetricAdaptor(Carbon(args.path, args.name, redis),
                      extract='load', question='question'),
        MetricAdaptor(Experiential(args.path, args.name, redis),
                      extract='load', question='question'),
        MetricAdaptor(Hydrology(args.path, args.name, redis),
                      extract='load', question='question'),
        MetricAdaptor(ImplementationCost(args.path, args.name,
                                         redis), extract='load', question='question'),
        MetricAdaptor(PeopleHouses(
            args.path, args.name, redis), extract='load', question='question'),
        MetricAdaptor(Infrastructure(
            args.path, args.name, redis), extract='load', question='question'),
        MetricAdaptor(Recreational(args.path, args.name, redis),
                      extract='load', question='question'),
        MetricAdaptor(RegionalEconomy(args.path, args.name, redis),
                      extract='load', question='question'),
    ]

    Util.answer_binary_questions(schemas)

    metrics = [s.name for s in schemas if s.active]

    Util.clear()
    Util.program_header()

    print("Extracting from %d Prescribed Burn Levels for:" % len(pb_levels))
    Util.rule()
    [print("%d. %s\n" % (i + 1, m)) for i, m in enumerate(metrics)]
    Util.rule()

    # Logging configuration
    LOG_PATH = Path(args.path).joinpath(EXTRACTION_LOG)
    print("Logging wil be saved at: ")
    print('%s' % (LOG_PATH))

    Util.clear()
    Util.program_header()
    Util.double_rule()
    print("Starting Extraction")
    Util.rule()

    widgets = [
        ' [Total ', progressbar.Timer(), ' ] ',
        progressbar.Bar(),
        ' (', progressbar.ETA(), ') ',
    ]

    total_lvls_pbar = progressbar.ProgressBar(range(79), widgets=widgets)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    for pb in total_lvls_pbar(pb_levels):
        schemas_pbar = progressbar.ProgressBar(range(79), widgets=[
            ' [PB: %s] ' % pb,
            ' [ ', progressbar.Timer(), ' ] ',
            progressbar.Bar(),
        ])
        [schema.extract(pb, SAVING) for schema in schemas_pbar(schemas)]

    Util.rule()
    print('Extraction complete.')
    Util.double_rule()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='Extractor.py', usage='%(prog)s [options]', description="Extract Web-Ready Data from Frost Post-Processing Outputs")
    parser.add_argument("path", help="Frost Outputs Path (our Input data).")
    parser.add_argument("name", help="Simulation Name")
    parser.add_argument(
        "lvls", help="The Prescribed Burn Levels to extract as comma separated list.")
    required = parser.add_argument_group()
    required.add_argument("-o", "--output-path",
                          help="Where to store outputs.")
    optional = parser.add_argument_group()
    optional.add_argument(
        "-y", "--yes", help="Accept defaults automatically", action="store_true")
    optional.add_argument(
        "-v", "--verbose", help="Increase output verbosity.", action="store_true")
    main(parser.parse_args())
