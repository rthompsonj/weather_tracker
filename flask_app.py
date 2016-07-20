from flask import Flask, request, render_template

app = Flask(__name__)

from forecaster import ForecastRetriever
FORECASTER = ForecastRetriever()
USER = 'rthompson'

icons = {
    'clear-day': 'day-sunny',
    'clear-night': 'night-clear',
    'rain': 'rain',
    'snow': 'snow',
    'sleet': 'sleet',
    'wind': 'strong-wind',
    'fog': 'fog',
    'cloudy': 'cloudy',
    'partly-cloudy-day': 'day-cloudy',
    'partly-cloudy-night': 'night-cloudy',
    'hail': 'hail',
    'thunderstorm': 'thunderstorm',
    'tornado': 'tornado'
}

@app.route('/', methods=['GET','POST'])
def index():
    rf = request.form

    if 'location' in rf:
        print rf['location'],type(rf['location'])
        FORECASTER.db.modify_user_location(USER, str(rf['location']))

    if 'REMOVE' in rf.keys():
        FORECASTER.db.remove_location_index(USER, int(rf['REMOVE']))
        
    forecast_data = FORECASTER.get_location_list(USER)        

    return render_template('index.html',
                           forecast_data = forecast_data,
                           current_loc = loc,
                           icons=icons)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
