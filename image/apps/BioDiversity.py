# Risk Metrics implemented in this file
#
# B  - Beta Diversity flora
# B1 - Change in species diversity
# B2 - Change in growth stage distribution
# B3 - Sensitivity of species diversity to sub-optimal growth stage distributions
# B4 - Single species abundance change
# B5 - Sensitivity of species diversity to sub-optimal growth stage distributions

import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import logging
logger = logging.getLogger(__name__)


class BioDiversity:

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Bio Diversity"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised Bio Object')
        logger.debug('Name: %s' % self.name)
        logger.debug('Path: %s' % self.path)

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    def load(self, pb, saving=False):
        if self.active:
            logger.debug('>>> Will extract %s' % self.name)
            if saving:
                logger.debug('>>> Will save %s' % self.name)

    layout = html.Div([
        html.H1('Biodiversity')
    ])
