# Risk Metrics implemented in this file
#
# FOR1 -
# AG1  -
# AG2  -
import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import logging

logger = logging.getLogger(__name__)


class RegionalEconomy:

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Regional Economy"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised ECO Object')
        logger.debug('Name: %s' % self.name)
        logger.debug('Path: %s' % self.path)

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    def load(self, pb, saving=False):
        if self.active:
            logger.debug('>>> Will extract %s' % self.name)
            if saving:
                logger.debug('>>> Will save %s' % self.name)

    layout = html.Div([])
