## cluster all violations, and add to the mongodb instance
import pymongo
import os
from urlparse import urlparse
import pandas as pd
import geojson
from time import strptime, mktime
from datetime import datetime
from sklearn.neighbors import DistanceMetric
from sklearn.cluster import DBSCAN

# get connection to the mongodb instance
MONGO_URI = 'mongodb://ben:nosreve@ds043210.mongolab.com:43210/heroku_app29696990'
conn = pymongo.Connection(MONGO_URI)
db = conn[urlparse(MONGO_URI).path[1:]]
collection = db.violationhistory

# open the violations in pandas
violations = pd.read_csv('all_violations.csv', index_col=0)
# group the violations by precinct
grouped = violations.groupby('precinct')

# date formatting method
def createdate(_violationtime, _violationdate):
    try: #try to format the date string, if not possible just return None
         # try to split the date string
        _m, _d, _y = _violationdate.split('/')
        # first append an 'M' to the time string
        _vtime = _violationtime + 'M'
        if len(_d) < 2:
            _d = '0' + _d
        if len(_m) < 2:
            _m = '0' + _m
        # combine both strings
        _dtstr = _vtime + ' ' + _m + ' ' + _d + ' ' + _y
        # return the corresponding date object
        _datetimeobj = datetime.fromtimestamp(mktime(strptime(_dtstr, '%H%M%p %m %d %y'))) 
        return _datetimeobj
    except ValueError:
        return None

# the list of violations to ultimately add to mongodb      
aggregated_list = []

# params for DBSCAN
_eps = .00025
_minpts = 3
# distance metric
dist = DistanceMetric.get_metric('euclidean')

for name, group in grouped:
    print "starting cluster of district " + str(name) 
    # zip the lat lon, into a single vector
    X = [list(i) for i in zip(group.latitude, group.longitude)]
    # generate pairwise distance matrix
    _pairwise = dist.pairwise(X)
    # generate clusters
    clusters = DBSCAN(eps=_eps, min_samples=_minpts, metric='precomputed').fit_predict(_pairwise)
    # save the clustered df
    clustered_df = group.copy()
    clustered_df['clusterid'] = clusters
    # go through the cluster-assigned dataframe and add to 'aggregated_list'
    for index, row in clustered_df.iterrows():
        unique_cluster = str(name) + "_" + str(row['clusterid'])
        _thedate = createdate(row['violationtime'], row['violationdate'])
        if _thedate is not None:
            # create the geojson object
            geoData = {'type' : 'Point', 'coordinates' : [row['latitude'], row['longitude']]}
            _violation = {'datetime':_thedate,
                    'weekday':_thedate.weekday(),
                    'hour':_thedate.time().hour,
                    'minute':_thedate.time().minute,
                    'precinct':row['precinct'],
                    'loc':geoData,
                    'clusterid':unique_cluster}
            aggregated_list.append(_violation)
    print "successfully clustered district " + str(name)

print "adding all clustered violations to mongodb"
# add the entire aggregated list to the mongo instance
db.violationhistory.insert(aggregated_list)
print "successfully clustered dataset!"