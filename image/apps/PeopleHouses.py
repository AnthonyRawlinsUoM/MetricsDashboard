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

from app import app
from apps.lib.version import meta
from dash.dependencies import Input, Output
from glob import glob as glob
from pathlib import Path
from tabulate import tabulate

import apps.util.Util as Util
import dash_core_components as dcc
import dash_html_components as html
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import xarray as xr

import logging
logger = logging.getLogger(__name__)

PPO_FOLDER = "post_processing_output"
EXTRACTIONS_PATH = "PeopleHouses"
phb_db_sql = """
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
            print('>>> Will extract %s' % self.name)
            if saving:
                print('>>> Will save %s' % self.name)

            ppo = Util.gather_ppo_dbs(self.path, self.scenario_name, pb)

            _burn_season = []
            _wild_season = []

            if len(ppo) == 0:
                print("Can't find any PPO files in %s " % self.path)
            else:
                batch_runs = sorted(
                    [int(b.split('/')[-3].split('pb')[-1]) for b in ppo], key=int)
                print('Found these batches.')
                [print(format(br, '03d')) for br in batch_runs]

            for bat in ppo:
                print('>>>> Loading: %s' % bat)

                r = Util.batch_from_path(bat)
                print('Replicate: %03d' % int(r))

                meta = Util.parse_proj_xml(bat.split(PPO_FOLDER)[
                                           0], self.scenario_name, r, pb)
                project_name = [
                    el.text for el in meta.findall('project_name')][0]
                project_descr = [
                    el.text for el in meta.findall('project_descr')][0]
                start_year_of_first_fireyear = int(
                    [el.text for el in meta.findall('start_year_of_first_fireyear')][0])
                start_year_of_last_fireyear = int(
                    [el.text for el in meta.findall('start_year_of_last_fireyear')][0])
                machines_in_files_root_dir = [
                    el.text for el in meta.findall('machines_in_files_root_dir')][0]

                print("Found FROST Project!")
    #             print("Name: %s" % project_name)
    #             print("Desc: %s" % project_descr)
    #             print("From: %s, To: %s" % (start_year_of_first_fireyear,
    #                                        start_year_of_last_fireyear))
    #             print("Using data from: %s" % machines_in_files_root_dir)
                now = datetime.datetime.now()

                meta_obj = {'project_name': project_name,
                            'project_descr': project_descr,
                            'start_year_of_first_fireyear': start_year_of_first_fireyear,
                            'start_year_of_last_fireyear': start_year_of_last_fireyear,
                            'machines_in_files_root_dir': machines_in_files_root_dir,
                            'processed_by': '',
                            'processed_on': now.isoformat(),
                            }
                meta_df = pd.DataFrame.from_dict(meta_obj, orient='index')

                print(tabulate(meta_df))

                df = Util.load_db_as_pandas(bat, phb_db_sql)

                if df is not None:
                    burn_batch_id = str(r)
                    df.set_index('scenario_id')

                    burn = df.iloc[1::2]
                    wild = df.iloc[::2]

    #                 print(tabulate(burn.T))
    #                 print(tabulate(wild.T))

                    b = xr.DataArray(burn, name='pb' + str(pb) + '_burn_season_batch' + burn_batch_id,
                                     coords={'Metrics_var': list(burn.T.index), 'years': range(start_year_of_first_fireyear, start_year_of_last_fireyear + 1)}, dims=['years', 'Metrics_var'])
                    w = xr.DataArray(wild, name='pb' + str(pb) + '_wild_season_batch' + burn_batch_id,
                                     coords={'Metrics_var': list(wild.T.index), 'years': range(start_year_of_first_fireyear, start_year_of_last_fireyear + 1)}, dims=['years', 'Metrics_var'])

                    b.attrs['burn_batch_id'] = burn_batch_id
                    b.attrs['pb_level'] = pb

                    _burn_season.append(b)
                    _wild_season.append(w)

            if len(_burn_season) > 0:
                burns = xr.concat(_burn_season, dim='batch')
                bname = 'PB_' + str(pb) + '_burn_seasons'
                burns.name = self.name
                burns.attrs = meta_obj
                burns.to_netcdf(Path(self.path).joinpath(
                    EXTRACTIONS_PATH).joinpath(bname + '.nc'), format='NETCDF4')

            if len(_wild_season) > 0:
                wilds = xr.concat(_wild_season, dim='batch')
                wname = 'PB_' + str(pb) + '_wild_seasons'
                wilds.name = self.name
                wilds.attrs = meta_obj
                wilds.to_netcdf(Path(self.path).joinpath(
                    EXTRACTIONS_PATH).joinpath(wname + '.nc'), format='NETCDF4')

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    def open(self):
        # load in the csvs
        # or load in the netcdfs
        # or load in the sqlites

        # create the DataFrame
        return True

    def generate_figure(self):

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
