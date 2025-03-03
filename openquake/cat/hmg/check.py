#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2020 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import toml
import pandas as pd
import datetime as dt
import geopandas as gpd

from openquake.baselib import sap
from geojson import LineString, Feature, FeatureCollection, dump


def get_features(cat, idx, idxsel):
    """
    :param cat:
    :param idx:
    :param idxsel:
    """
    features = []

    lon1 = float(cat.loc[idx, 'longitude'])
    lat1 = float(cat.loc[idx, 'latitude'])
    tmp = cat.loc[idx, 'eventID']
    if type(tmp).__name__ == 'str':
        evid = tmp
    elif type(tmp).__name__ in ['int', 'int64', 'int32']:
        evid = "{:d}".format(cat.loc[idx, 'eventID'])
    else:
        fmt = "Unsupported format for EventID: {:s}"
        raise ValueError(fmt.format(type(tmp).__name__))

    for i in idxsel:
        lon2 = float(cat.loc[i, 'longitude'])
        lat2 = float(cat.loc[i, 'latitude'])
        line = LineString([(lon1, lat1), (lon2, lat2)])
        features.append(Feature(geometry=line, properties={"eventID": evid}))

    return features


def process(cat, sidx, delta_ll, delta_t, fname_geojson):
    """
    :param cat
        A pandas geodataframe instance containing a homogenised catalogue as
        obtained from :method:`openquake.cat.hmg.merge.hmg.process_dfs`
    :param sidx:
        Spatial index for the geodataframe as obtained by `gdf.sindex`
    :param delta_ll:
        A float defining the longitude/latitude tolerance used for checking
    :param delta_t:
        A float [in seconds] the time tolerance used to search for duplicated
        events.
    :param fname_geojson:
        Name of the output .geojson file which will contains the lines
        connecting the possibly duplicated events.
    """

    features = []
    found = set()
    delta_t = dt.timedelta(seconds=delta_t)
    cnt = 0

    from tqdm import tqdm
    import numpy as np
    # Loop over the earthquakes in the catalogue
    # datetime can only cover 548 years starting in 1677
    # general advice will be to exclude historic events and 
    # add those later
    subcat = cat[cat['year']>1800]
    nat_idx = np.where(pd.isnull(subcat.loc[:, 'datetime'])==False)[0].tolist()
    for index, row in tqdm(subcat.iterrows()):

        # Select events that occurred close in space
        minlo = row.longitude - delta_ll
        minla = row.latitude - delta_ll
        maxlo = row.longitude + delta_ll
        maxla = row.latitude + delta_ll
        idx_space = list(sidx.intersection((minlo, minla, maxlo, maxla)))

        tmp = abs(subcat.loc[:, 'datetime'] - row.datetime) < delta_t
        idx_time = list(tmp[tmp].index)

        # Find the index of the events that are matching temporal and spatial
        # constraints
        idx = (set(idx_space) & set(idx_time)) - found

        if len(idx) > 1:
            cnt += 1
            features.extend(get_features(subcat, index, idx))
            for i in idx:
                found.add(i)

    # Create the geojson file
    feature_collection = FeatureCollection(features)
    with open(fname_geojson, 'w') as fou:
        dump(feature_collection, fou)

    # Info
    if cnt > 0:
        print("Created file: {:s}".format(fname_geojson))

    return cnt


def check_catalogue(catalogue_fname, settings_fname):
    """
    :fname catalogue_fname:
        An .h5 file with the homogenised catalogue
    :fname settings_fname:
        The name of a file containing the settings used to create a catalogue
    """

    print("Checking catalogue")

    # Read configuration
    settings = toml.load(settings_fname)

    # Load the catalogue
    _, file_extension = os.path.splitext(catalogue_fname)
    if file_extension in ['.h5', '.hdf5']:
        cat = pd.read_hdf(catalogue_fname)
    elif file_extension == '.csv':
        cat = pd.read_csv(catalogue_fname)
    else:
        raise ValueError("File format not supported")

    # Getting a geodataframe
    if type(cat).__name__ != 'GeoDataFrame':
        cat = gpd.GeoDataFrame(cat, geometry=gpd.points_from_xy(cat.longitude,
                                                                cat.latitude))

    # Create the spatial index
    sindex = cat.sindex

    # Add datetime field
    if "datetime" not in cat.keys():
        cat['datetime'] = pd.to_datetime(cat[['year', 'month', 'day', 'hour',
                                              'minute', 'second']], errors = 'coerce')

    # Set filename
    out_path = settings["general"]["output_path"]
    geojson_fname = os.path.join(out_path, "check.geojson")

    # Processing the catalogue
    delta_ll = settings["general"]["delta_ll"]
    delta_t = settings["general"]["delta_t"]
    nchecks = process(cat, sindex, delta_ll, delta_t, geojson_fname)

    return nchecks


def main(argv):
    """ """

    p = sap.Script(check_catalogue)
    msg = 'Name of a .h5 file containing the homogenised catalogue'
    p.arg(name='catalogue_fname', help=msg)
    p.arg(name='settings_fname', help='.toml file with the model settings')
    p.arg(name='out_folder', help='path of the output folder')

    if len(argv) < 1:
        print(p.help())
    else:
        p.callfunc()


if __name__ == "__main__":
    main(sys.argv[1:])
