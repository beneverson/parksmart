## cluster the violations in the live mongodb collection
import pymongo

MONGO_URI = os.environ.get('MONGOLAB_URI')
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
    while i < len(_neighborDocs):  # go thru all neighbor docs
        _neighbor = _neighborDocs[i]
        # if this document was not visited
        if _neighbor['_id'] not in visitedIds:
            # mark as visited by adding to the lookup table
            visitedIds.append(_neighbor['_id'])
            # find documents near '_neighbor' 
            newNeighborDocs = list(collection.find({'loc' : {'$near' : {'$geometry': _neighbor['loc'], 
                                                                        '$maxDistance' : _maxDistance} } , 'precinct': _precinctID}))
            # expand the cluster if we can
            if len(newNeighborDocs) >= _minPoints:
                _neighborDocs.extend(newNeighborDocs) 
        # if the neigbor has not yet been added to any cluster, add it to the current one
        if 'clusterid' not in _neighbor:
            collection.update({'_id' : _neighbor['_id']}, 
                              {'$set':{'clusterid' : clustername}}, 
                              upsert=False, multi=False)
        # increment the index
        i += 1
    return

def DBSCAN_Mongo(_collection, _maxDistance, _minPoints, _precinctID):
    # init the clusterid
    clusterID = 0
    # find each doc in the DB
    findall_cursor = list(_collection.find()) # find all docs in the db
    
    for _doc in findall_cursor:
        if _doc['_id'] not in visitedIds:
            # mark as visited by adding to the lookup table
            visitedIds.append(_doc['_id'])
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