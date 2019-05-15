# Risk Metrics implemented in this file
#
# RS1  - Loss of mapped recreational facilities, sports grounds, camp grounds etc.

import pandas as pd
from pathlib import Path
from glob import glob as glob
import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import logging
logger = logging.getLogger(__name__)


class Recreational:

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Recreational"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised REC Object')
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
        html.H1('Recreational')
    ])
