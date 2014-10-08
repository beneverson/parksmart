## cluster the violations in the live mongodb collection
import pymongo
import os
from urlparse import urlparse

MONGO_URI = 'mongodb://ben:nosreve@ds043210.mongolab.com:43210/heroku_app29696990'
conn = pymongo.Connection(MONGO_URI)
db = conn[urlparse(MONGO_URI).path[1:]]
collection = db.violationhistory

# 'expand cluster' method for dbscan implementation
def expandCluster(_doc, _neighborDocs, _clusterId, _maxDistance, _minPoints, _precinctID):
    # add doc to cluster 
    clustername = str(_clusterId) + "_" + str(_precinctID)
    collection.update({'_id' : _doc['_id']}, 
                              {'$set':{'clusterid' : clustername}}, 
                              upsert=False, multi=False)
   
    i = 0 # declare an index into _neighborDocs
    while _neighborDocs:  # go thru all neighbor docs
        _neighbor = _neighborDocs.pop(0)
        # if this document was not visited
        if str(_neighbor['_id']) not in visitedIds:
            # mark as visited by adding to the lookup table
            visitedIds.append(str(_neighbor['_id']))
            # find documents near '_neighbor' 
            newNeighborDocs = list(collection.find({'loc' : {'$near' : {'$geometry': _neighbor['loc'], 
                                                                        '$maxDistance' : _maxDistance} } , 'precinct': _precinctID}))
            # expand the cluster if we can
            if len(newNeighborDocs) >= _minPoints:
                # create a new list that contains only neigbors we haven't seen before
                differentNeighborDocs = [aDoc for aDoc in newNeighborDocs if not any(str(_d['_id']) == str(aDoc['_id']) for _d in _neighborDocs)]
                _neighborDocs.extend(differentNeighborDocs) 
        # if the neigbor has not yet been added to any cluster, add it to the current one
        if 'clusterid' not in _neighbor:
            collection.update({'_id' : _neighbor['_id']}, 
                              {'$set':{'clusterid' : clustername}}, 
                              upsert=False, multi=False)
    return

def DBSCAN_Mongo(_collection, _maxDistance, _minPoints, _precinctID):
    # init the clusterid
    clusterID = 0
    # find each doc in the DB
    findall_cursor = list(_collection.find()) # find all docs in the db
    
    for _doc in findall_cursor:
        if str(_doc['_id']) not in visitedIds:
            # mark as visited by adding to the lookup table
            visitedIds.append(str(_doc['_id']))
            # find all the points in this area
            neighborDocs = list(collection.find({'loc' : {'$near' : {'$geometry': _doc['loc'], 
                                                                        '$maxDistance' : _maxDistance} }, 'precinct': _precinctID}))
            if len(neighborDocs) < _minPoints:
                collection.update({'_id' : _doc['_id']}, 
                              {'$set':{'clusterid' : 'NOISE'}}, 
                              upsert=False, multi=False)
            else:
                clusterID += 1
                expandCluster(_doc, neighborDocs, clusterID, _maxDistance, _minPoints, _precinctID)
    
    return
    
# first get a list of the distinct precincts in the collection
precincts = collection.distinct('precinct')
for _precinct in precincts:
    # lookup table for visited docs in the database
    visitedIds = []
    print "started cluster of precinct " + str(_precinct)
    DBSCAN_Mongo(collection, 20, 3,_precinct)
    print "finished clustering precinct: " + str(_precinct)