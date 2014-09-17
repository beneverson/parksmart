from flask import Flask, request, jsonify
import ParkSmart

app = Flask(__name__)

@app.route('/')
def index():
    # render the html page
    return "Hello, world!"
    
@app.route('/parksmart/api/getviolations/', methods=['GET'])
def getviolations():
    # grab lat, lon, and radius from the request object
    _lat = request.args.get('lat')
    _lon = request.args.get('lon')
    _radius = request.args.get('radius')
    # query the database
    _violations = ParkSmart.getViolations(_lat, _lon, _radius) 
    # return the json-ified data                                                                  
    return jsonify(data=_violations)
    
if __name__ == '__main__':
    app.run(debug=True)