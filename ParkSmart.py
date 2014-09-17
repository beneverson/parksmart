from pymongo import MongoClient
import json
from bson import json_util

client = MongoClient()
db = client.nycparking

def getViolations(_lat, _lon, _rad, _limit = 100):
  
    # retrieve 10 violations near _lat, _lon within a radius of _rad 
    _cursor = db.violationhistory.find({ 'loc': { '$geoWithin': { '$center' : [ [float(_lon), float(_lat)], float(_rad) ] } }}).limit(_limit)
    
    _violations = []
    for doc in _cursor: # remove the id element (non-serializable)
        doc.pop('_id') 
        _violations.append(doc)
        
    return _violations # re