from flask import Flask, request, render_template, url_for, session, redirect

app = Flask(__name__)

from forecaster import ForecastRetriever
FORECASTER = ForecastRetriever()

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


@app.route('/login', methods=['POST'])
def login():
    user = FORECASTER.db.get_user(request.form['username'].lower())
    if user is None:
        return 'No user by that name exists'
    if not FORECASTER.db.verify_password(user['password'], request.form['password']):
        return 'Incorrect password for %s!' % request.form['username']

    session['username'] = request.form['username'].lower()
    return redirect(url_for('weather'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print 'POSTING'
        user = FORECASTER.db.get_user(request.form['username'].lower())
        if user is not None:
            return 'User with that name already exists!'
        FORECASTER.db.add_user(request.form['username'].lower(),
                               request.form['password'])
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/')
def index():
    print session
    if 'username' in session:
        return redirect(url_for('weather'))
    return render_template('index.html')
    
@app.route('/weather', methods=['GET','POST'])
def weather():

    USER = session['username']
    
    rf = request.form
    
    if 'location' in rf:
        print rf['location'],type(rf['location'])
        FORECASTER.db.modify_user_location(USER, str(rf['location']))

    if 'REMOVE' in rf.keys():
        FORECASTER.db.remove_location_index(USER, int(rf['REMOVE']))
        
    forecast_data = FORECASTER.get_location_list(USER)

    return render_template('weather.html',
                           forecast_data = forecast_data,                           
                           icons=icons)


if __name__ == '__main__':
    app.secret_key = 'templeofdoom'
    app.run(host='0.0.0.0', debug=True)
    
