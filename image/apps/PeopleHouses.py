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
import numpy as np
import pandas as pd
from pathlib import Path
from glob import glob as glob
import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import plotly.plotly as py
import plotly.graph_objs as go

import logging
logger = logging.getLogger(__name__)

phib_db_sql = """
SELECT * FROM PeopleHouseLoss
"""


# For Testing purposes only...
df = pd.DataFrame(np.random.rand(100, 6) * 100, columns=[
                  'PB 0', 'PB 1', 'PB 2', 'PB 3', 'PB 5', 'PB 10'])

sample_data = []

pb_colours = ["#fde725",
              "#90d743",
              "#35b779",
              "#21918c",
              "#31688e",
              "#443983",
              "#440154"
              ]
colour_index = 0
for col in df.columns:
    sample_data.append(
        go.Box(
            y=df[col],
            name=col,
            marker=dict(color=pb_colours[colour_index]),
            boxmean=True,
            showlegend=True
        )
    )
    colour_index = colour_index + 1


class PeopleHouses:
    """
    """

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "PeopleAndHouses"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised PH Object')
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
                ncname = 'ph_%s.nc' % pb
                ncpath = str(Path(self.path).joinpath(ncname))
                ds.to_xarray().to_netcdf(ncpath, format='NETCDF4')
                logger.info('Wrote %s to %s' % (ncname, self.path))
                ds.to_csv(str(Path(self.path).joinpath('ph_%s.csv' % pb)))

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    layout = html.Div([
        html.H1('People & Houses'),
        dcc.Graph(
            id='example-graph',
            figure={
                'data': sample_data,
                'layout': {
                    'title': 'House Loss at varying Prescribed Burning Levels'
                }
            }
        )
    ])
