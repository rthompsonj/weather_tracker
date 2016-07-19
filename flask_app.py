from flask import Flask, request, render_template

app = Flask(__name__)

from forecaster import ForecastRetriever
FORECASTER = ForecastRetriever()
FORECASTER.set_location('austin')

@app.route('/', methods=['GET','POST'])
def index():
    rf = request.form
    if 'location' in rf:
        FORECASTER.set_location(rf['location'])
    return render_template('index.html',
                           day_data = FORECASTER.current_data['daily']['data'],
                           current_loc = FORECASTER.current_location)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
