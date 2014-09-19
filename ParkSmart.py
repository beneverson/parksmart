import os
import pymongo
import json
from bson import json_util
from urlparse import urlparse

#MONGO_URL = os.environ.get('MONGOHQ_URL')
MONGO_URL = 'mongodb://ben:nosreve@kahana.mongohq.com:10098/app29696990'

if MONGO_URL:
    conn = pymongo.Connection(MONGO_URL)
    
    db = conn[urlparse(MONGO_URL).path[1:]]
    
else: 
    client = pymongo.MongoClient()
    
    db = client.nycparking

def getViolations(_lat, _lon, _rad, _limit = 10):
    
    # retrieve 10 violations near _lat, _lon within a radius of _rad 
    _cursor = db.violationhistory.find({ 'loc': { '$geoWithin': { '$center' : [ [float(_lon), float(_lat)], float(_rad) ] } }}).limit(_limit)
    
    _violations = []
    for doc in _cursor: # remove the id element (non-serializable)
        doc.pop('_id') 
        _violations.append(doc)
        
    return _violations # re