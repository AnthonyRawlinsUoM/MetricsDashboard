
from pathlib import Path
from glob import glob as glob
from extractor.Ignition import Ignition
import logging
logger = logging.getLogger(__name__)


class Ignitions:
    """
    """

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Ignitions"
        self.path = path
        self.scenario_name = scenario_name

    def load(self, pb, saving=False):
        if self.active:
            logger.debug('>>> Will extract %s' % self.name)
            if saving:
                logger.debug('>>> Will save %s' % self.name)

            """
             TODO -> take path components from instance parameters and
             dynamically generate paths and globs using OS-agnostic calls
             to pathlib. Ensure Windows compatability.
            """
            scn = str(Path(self.path).joinpath(
                self.scenario_name)) + "_{}*".format(pb)
            batch_list = sorted(
                glob(scn + "/centralhigh_*/regsim_ignitions.txt"))
            for bat in batch_list:
                replicate = Util.bid(bat)
                with open(bat, 'r') as ig:
                    line_count = 0
                    fdata = ig.read()
                    for c in fdata.split('\n'):
                        line_count += 1
                        if c != '':
                            try:
                                line_place = '[line: %10d]' % (line_count)
                                i = Ignition(c, bat + line_place)
                                if i.store(pb, replicate, redis):
                                    logger.debug(line_place, '[OK]', str(i))
                                else:
                                    logger.debug(line_place, '[XX]', c)
                            except KeyError as e:
                                logger.error('Ignition Parsing Error')

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)
