# Risk Metrics implemented in this file
#
# HH1   - Estimated loss of life
# HH1a  - Loss of life (based on 4.2million dollars per life)
# HH2   - Estimated loss of houses (Tolhurst & Chong 2011)
# HH2a  - Loss of house (t.b.d. NEXIS)
#
# ??    - Infrastructure - schools, hospitals etc
#
# NICH1 - Loss of mapped community structures
# NICH2 - House loss (see above)

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

phib_db_sql = """
SELECT *
FROM Infrastructure
"""


class Infrastructure:
    """
    """

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Infrastructure"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised Infrastructure Object')
        logger.debug('Name: %s' % self.name)
        logger.debug('Path: %s' % self.path)

    def load(self, pb, saving=False):
        if self.active:
            logger.debug('>>> Will extract %s' % self.name)
            if saving:
                logger.debug('>>> Will save %s' % self.name)

            b_id = Util.bid(self.path)
            logger.debug('>>>>> Loading PHI Data from: %s' % b_id)
            scn = str(Path(self.path).joinpath(
                self.scenario_name)) + "_{}*".format(pb)
            logger.debug('Built the search in: %s' % scn)

            batch_list = sorted(glob(
                scn + "/centralhigh_*/post_processing_output/phibc_post_proc_results.sqlite"))
            [logger.debug('Found BatchList: %s' % b) for b in batch_list]

            batch_runs = sorted([Util.bid(b) for b in batch_list], key=int)
            [logger.debug('Found Batch: %s' % b) for b in batch_runs]
            _to = []

            for bat in batch_list:
                logger.debug('>>>> Loading: %s' % bat)
                df = Util.load_db_as_pandas(bat, phib_db_sql)
                if df is not None:
                    df['batch_id'] = b_id
                    df.reset_index()
                    _to.append(df)
            if saving:
                ds = pd.concat(_to)
                # ds = xr.open_mfdataset()
                ncname = 'inf_%s.nc' % pb
                ds.to_xarray().to_netcdf(str(Path(self.path).joinpath(ncname)), format='NETCDF4')
                logger.info('Wrote %s to %s' % (ncname, self.path))

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    layout = html.Div([
        html.H1('Infrastructure')
    ])
