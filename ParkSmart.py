import os
import pymongo
import json
from bson import json_util
from urlparse import urlparse
import datetime

#MONGO_URL = os.environ.get('MONGOHQ_URL')
MONGO_URL = 'mongodb://ben:nosreve@kahana.mongohq.com:10098/app29696990'

if MONGO_URL:
    conn = pymongo.Connection(MONGO_URL)
    
    db = conn[urlparse(MONGO_URL).path[1:]]
    
else: 
    client = pymongo.MongoClient()
    
    db = client.nycparking

def getViolations(_lat, _lon, _rad, _limit = 1000):
    
    # retrieve 10 violations near _lat, _lon within a radius of _rad 
    _cursor = db.violationhistory.find({ 'loc': { '$geoWithin': { '$center' : [ [float(_lon), float(_lat)], float(_rad) ] } }}).limit(_limit)
    
    _violations = []
    for doc in _cursor: # remove the id element (non-serializable)
        doc.pop('_id') 
        _violations.append(doc)
        
    return _violations # re

def getGoodSpots(_lat, _lon, _rad):
    
    # retrieve all the tickets that were issued near _lat and _lon, within _rad, 
    # and were already issued on this weekday
    
    # first get a cursor for all tickets within _rad of _lat, _lon
    # issued on the current weekday
    # at or before the current hour
    _cursorlist = list(db.violationhistory.find({ 'loc': { '$geoWithin': { '$center' : [ [float(_lon), float(_lat)], float(_rad) ] } }, 
                                     'weekday': datetime.datetime.today().weekday(),
                                        'hour': { '$lte': datetime.datetime.today().time().hour }}))
    
    _violations = []
    i = 0
    # filter the results 
    for doc in _cursorlist:
        i += 1
        # if the violation occured at the current hour, make sure it occured before the current minute
        if doc['hour'] != datetime.datetime.today().time().hour or (doc['hour'] == datetime.datetime.today().time().hour and doc['minute'] < datetime.datetime.today().time().minute):
            doc.pop('_id') # remove the mongo id tag, not serializable
            _violations.append(doc) # append the violation to the _violations list
            
    print "Reached end of cursor loop."     
    return _violations 