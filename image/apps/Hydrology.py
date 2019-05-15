# Risk Metrics implemented in this file
#
# W1  - Gross Water Quality Index
# W2  - Net Water Quality Index
# W3  - Gross Streamflow Index
# W4  - Net Streamflow Index

from glob import glob as glob
import xarray as xr

from pathlib import Path
import apps.util.Util as Util

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import json
import logging
logger = logging.getLogger(__name__)


class Hydrology:
    """
    """
    HYDRO_FILE_NAME = "hydro_machine_results.sqlite"

    def __init__(self, path, scenario_name, redis):
        self.redis = redis
        self.active = False
        self.name = "Hydrology"
        self.path = path
        self.scenario_name = scenario_name
        self._to = []
        logger.debug('Initialised HYDRO Object')
        logger.debug('Name: %s' % self.name)
        logger.debug('Path: %s' % self.path)

    def load(self, pb, saving=False):
        if self.active:
            logger.debug('>>> Will extract %s' % self.name)
            hydro = None
            if saving:
                logger.debug('>>> Will save %s' % self.name)

            """
             TODO -> take path components from instance parameters and
             dynamically generate paths and globs using OS-agnostic calls
             to pathlib. Ensure Windows compatability.
            """
            scn = str(Path(self.path).joinpath(
                self.scenario_name)) + "_{}*".format(pb)
            batch_list = sorted(list(set(list(glob(str(Path(scn)
                                                       .joinpath("centralhigh_*")
                                                       .joinpath("post_processing_output")
                                                       .joinpath("hydro_machine_results.sqlite")))))))

            batch_runs = sorted([Util.bid(b) for b in batch_list], key=int)

            # logger.debug(batch_list)
            # logger.debug(batch_runs)

            select_all_from = "SELECT * FROM "

            for replicate in batch_list:
                logger.debug('>>>> Loading: %s' % replicate)
                hydro = None

                for i in range(2, 100, 2):
                    b_id = Util.bid(replicate)
                    try:
                        logger.debug('Fire year:{}'.format(i))
                        grid_info = Util.load_db_as_pandas(
                            replicate, "{}General".format(select_all_from))

                        wy = Util.load_db_as_pandas(
                            replicate, "%sWaterYieldResults_AfterScenario%s" % (select_all_from, i))

                        options = dict(
                            rows=grid_info['simgrid_row_count'][0],
                            cols=grid_info['simgrid_col_count'][0],
                            left=grid_info['simgrid_left'][0],
                            bottom=grid_info['simgrid_bottom'][0],
                            cell_size=grid_info['simgrid_cell_size'][0],
                            column='simcell_index'
                        )
                        longs, lats = Util.convert_simcell_index_to_latlong(
                            wy, **options)
                        polygons = Util.convert_simcell_index_to_cell_polygon(
                            wy, **options)

                        wy['long'] = longs
                        wy['lat'] = lats
                        wy['coordinates'] = polygons
                        # wy = wy.set_index(['simcell_index', 'catchment_id'])
                        xwy = wy.to_xarray()

                        # TODO get study period start and add i/2 (because 0-100 is off/on fireseason, so ith are fireseasons)
                        # Start year + (i/2) years
                        xwy['time'] = (i / 2)

                        key = "WaterYieldResults_AfterScenario%s" % i

                        # TODO -> make PB in properties dynamic
                        features = [{"type": "Feature",
                                     "properties": {
                                         "title": catchment_id,
                                         "pb_level": "PB %s" % (pb),
                                         "batch": b_id,
                                         "time": "%s" % i,
                                         "mean_annual_streamflow": mean_annual_streamflow,
                                         "catchment_id": catchment_id,
                                         "simcell_index": simcell_index,
                                         "lat": lat,
                                         "lon": long,
                                         "metric": "wateryield"
                                     },
                                     "geometry": {
                                         "type": "Polygon",
                                         "coordinates": coordinates
                                     }
                                     } for (simcell_index, catchment_id, mean_annual_streamflow, long, lat, coordinates) in wy.values]

                        cached_ok = self.redis.set(key, json.dumps(
                            {'type': 'FeatureCollection', 'features': features}))

                        ds2 = xwy.set_coords(
                            ['time', 'catchment_id', 'simcell_index'])

                        if hydro is None:
                            hydro = ds2
                        else:
                            # Do merge
                            hydro = xr.concat([hydro, ds2], 'year_n')
                    # except FileError as e:
                    #    logger.error('Exception occured during processing Water Yield Scenario replicate: %s, Batch: %s' % (i, b_id))
                    #    logger.error(e)
                    except ValueError as e:
                        logger.error(e)

            if hydro is not None:
                hydro['batch_pb'] = pb
                # _to.append(hydro)
                if saving:
                    hydro.to_netcdf(
                        str(Path(self.path).joinpath('hydro_%s.nc' % pb)))

    def question(self):
        return "Would you like to extract {} Metrics?".format(self.name)

    layout = html.Div([
        html.H1('Hydrology')
    ])
