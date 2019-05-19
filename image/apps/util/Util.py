
from dash.dependencies import Input, Output
from glob import glob as glob
from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
import datetime
import math
import numpy as np
import os
import pandas as pd
import pyproj
import shutil
import sqlite3
import xarray as xr
import xml.etree.ElementTree

import logging
logger = logging.getLogger(__name__)


PPO_FOLDER = "post_processing_output"
PHI_FILE = "phibc_post_proc_results.sqlite"

epsg3857 = pyproj.Proj("+init=EPSG:3857")
vicgrid94 = pyproj.Proj("+init=EPSG:3111")
wgs84 = pyproj.Proj("+init=EPSG:4326")


def get_pb_levels(path, name):
    return sorted(list(map(extract_pb_from_paths, glob(str(Path(path).joinpath(name)) + "_*"))), key=int)


def convert_simcell_index_to_latlong(df, column, rows, cols, left, bottom, cell_size):
    i = df[[column]].values
    x, y = np.divmod(i, cols)
    x_m = x * cell_size
    y_m = y * cell_size
    x_meters = left + x_m
    y_meters = bottom - y_m
    longs, lats = pyproj.transform(vicgrid94, wgs84, x_meters, y_meters)
    return longs, lats


def convert_simcell_index_to_cell_polygon(df, column, rows, cols, left, bottom, cell_size):
    i = df[[column]].values

    return [
        [pyproj.transform(vicgrid94, wgs84, left + (x[0] * cell_size),     bottom - (y[0] * cell_size)),
         pyproj.transform(vicgrid94, wgs84, left
                          + ((x[0] - 1) * cell_size), bottom - (y[0] * cell_size)),
         pyproj.transform(vicgrid94, wgs84, left +
                          ((x[0] - 1) * cell_size), bottom - ((y[0] + 1) * cell_size)),
         pyproj.transform(vicgrid94, wgs84, left +
                          (x[0] * cell_size),     bottom - ((y[0] + 1) * cell_size)),
         pyproj.transform(vicgrid94, wgs84, left +
                          (x[0] * cell_size),     bottom - (y[0] * cell_size))
         ] for (x, y) in [np.divmod(a, cols) for a in i]
    ]


def answer_binary_questions(schemas):

    ql = len(schemas)

    for i, q in enumerate(schemas):
        good_response = False
        while(not good_response):
            clear()
            program_header()
            print('Question %d of %d' % (i + 1, ql))
            rule()
            print(q.question())
            rule()
            r = input("[Y/n]: ")
            if r == "" or r == "":
                q.active = True
                good_response = True
            if r == "Y" or r == "y":
                q.active = True
                good_response = True
            if r == "N" or r == "n":
                q.active = False
                good_response = True


def pb_as_csv(ds, pb):
    pb_to_csv(ds, pb)
    return ds.sel(PB=pb).to_dataframe().to_csv()


def pb_to_csv(ds, pb):
    with open('./data/examplePB%s.csv' % pb, 'w') as f:
        ds.sel(PB=pb).to_dataframe().to_csv(f)


def hash_key(item):
    return str(hash(str(item)))


def bid(p):
    return p.split('pb')[-1].split('/')[0]


def batch_id(p):
    return p.split('_')[-1]


def load_db_as_xarray(p):
    return xr.Dataset.from_dataframe(load_db_as_pandas(p))


def load_db_as_pandas(db, sql):
    if not Path(db).is_file():
        print('File not found!')
    else:
        # logger.debug('Opening: %s' % db)
        dat = sqlite3.connect(db)
        query = dat.execute(sql)
        cols = [column[0]
                for column in query.description if column[0] is not 'scenario_id']
#         print(cols)
        d = query.fetchall()
        results = pd.DataFrame.from_records(
            data=d, columns=cols, coerce_float=True)
        return results


def csv_this(list_of_df):
    csv = ''
    for df in list_of_df:
        csv += df.to_csv()
    return csv


def rule():

    columns, lines = shutil.get_terminal_size((80, 20))
    print("-" * (columns - 1))


def double_rule():
    columns, lines = shutil.get_terminal_size((80, 20))
    print("=" * (columns - 1))


def program_header():
    ascii_art = """
    ____  __________    __  ___     __       _          
   / __ \/ ___/ ___/   /  |/  /__  / /______(_)_________
  / / / /\__ \\__ \   / /|_/ / _ \/ __/ ___/ / ___/ ___/
 / /_/ /___/ /__/ /  / /  / /  __/ /_/ /  / / /__(__  ) 
/_____//____/____/  /_/  /_/\___/\__/_/  /_/\___/____/  
    """
    columns, lines = shutil.get_terminal_size((80, 20))
    ctr = "DSS Metrics Viewer v1.0"
    r = int(math.floor(((columns) - (len(ctr) + 2)) / 2))
    # print("="*r, ctr, "="*(columns-(r + len(ctr) + 2)))
    print(ascii_art)

# define our clear function


def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


def readable(p):
    return os.access(Path(p), os.R_OK)


def writeable(p):
    return os.access(Path(p), os.W_OK)


def extract_pb_from_paths(pathlist):
    return pathlist.split('_')[-1].replace('pb', '')


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]

 # Body
        + [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def parse_proj_xml(resource):
    obj = untangle.parse(resource)
    return obj


def pb_suffix(pb):
    return "_{}pb".format(pb)


def batch_subfolder(scenario_name, pb):
    return scenario_name.replace('2018', '18') + pb_suffix(pb) + "*"


def activate(schemas, n):
    [s for s in schemas if s.name == n][0].active = True
    for s in schemas:
        if s.name != n:
            s.active = False


def batch_from_path(bat):
    return int(bat.split('/')[-3].split('pb')[-1])


def parse_proj_xml(batch_folder, scenario_name, batch, pb):
        # Project XML
    proj_file = scenario_name.replace(
        '2018', '18') + pb_suffix(pb) + format(batch, "03d") + ".frost.proj"

    # Determine Path to Project XML file
    path_to_proj = str(Path(batch_folder).joinpath(proj_file))

    if not Path(path_to_proj).is_file():
        print('Project folders path to Project File not found.')

    e = xml.etree.ElementTree.parse(path_to_proj).getroot()
    return e


def gather_ppo_dbs(root, scenario_name, pb):
    """
    """

    # Folder heirarchy conventions
    heirarchy = Path(root).joinpath(scenario_name).joinpath(scenario_name + pb_suffix(pb)
                                                            ).joinpath(batch_subfolder(scenario_name, pb))

    search = str(heirarchy.joinpath(PPO_FOLDER).joinpath(PHI_FILE))

    print("Looking in: %s" % (search))
    # Get all paths
    return sorted(glob(search))
