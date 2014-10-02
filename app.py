from flask import Flask, request, jsonify, render_template
import geojson
import ParkSmart

app = Flask(__name__)

@app.route('/')
def index():
    # render the html page
    return render_template('index.html')
    
@app.route('/parksmart/api/getviolations/', methods=['GET'])
def getviolations():
    # grab lat, lon, and radius from the request object
    _lat = request.args.get('lat')
    _lon = request.args.get('lon')
    _radius = request.args.get('radius')
    # query the database
    _violations = ParkSmart.getViolations(_lat, _lon, _radius)
     
    # convert this to geojson
    geojson_violations = []
    for doc in _violations:
        geojson_violations.append(geojson.Feature(geometry=geojson.Point(doc['loc'])))
        
    # return the data as geojson                                                                  
    return jsonify(data=geojson_violations)
    
@app.route('/parksmart/api/getgoodspots/', methods=['GET'])
def getgoodspots():
    # grab lat, lon, and radius from the request object
    _lat = request.args.get('lat')
    _lon = request.args.get('lon')
    _radius = request.args.get('radius')
    # query the database
    _violations = ParkSmart.getGoodSpots(_lat, _lon, _radius)
    
    print "Reached!!"
     
    # convert this to geojson
    geojson_violations = []
    for doc in _violations:
        geojson_violations.append(geojson.Feature(geometry=geojson.Point(doc['loc'])))
        
    # return the data as geojson                                                                  
    return jsonify(data=geojson_violations)
    
if __name__ == '__main__':
    app.run(debug=True)