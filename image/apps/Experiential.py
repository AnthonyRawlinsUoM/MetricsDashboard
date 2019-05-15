# Risk Metrics implemented in this file
#
# E1  - Visual aesthetics of accessible forests
# E2  - Visual aesthetics of burnt forest
# E3  - Opportunity for people to experience flora and fauna
import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import logging

logger = logging.getLogger(__name__)


class Experiential:

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Experiential"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised EXP Object')
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
        html.H1('Experiential')
    ])
