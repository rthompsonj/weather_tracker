from flask import Flask, request, render_template

app = Flask(__name__)

from forecaster import ForecastRetriever
FORECASTER = ForecastRetriever()
#FORECASTER.set_location('austin')
loc = 'austin'

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
        loc = rf['location']
        #FORECASTER.set_location(rf['location'])
    else:
        loc = 'austin'

    return render_template('index.html',
                           #day_data = FORECASTER.current_data['daily']['data'],
                           #current_loc = FORECASTER.current_location,
                           day_data = FORECASTER.get_forecast(loc)['daily']['data'],
                           current_loc = loc,
                           icons=icons)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
