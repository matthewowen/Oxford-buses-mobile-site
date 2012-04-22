from backend import *

import json as simplejson

app = Flask(__name__)

# UTILITIES

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# ERRORS, PROBLEMS, STATIC

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	return render_template('500.html'), 500

@app.route('/no-location')
def no_location():
	return render_template('no_location.html')

@app.route('/about')
def about():
	return render_template('about.html')

# RESULTS

@app.route('/stops/<latitude>+<longitude>')
def stops(latitude, longitude):
	loc_info = get_stops(latitude, longitude, 0)
	options = loc_info[0]
	more = loc_info[-1]
	return render_template('stop_list.html', stop_list=options, more=more, userlat=latitude, userlong=longitude)

@app.route('/ajax/stops/<latitude>+<longitude>/<int:offset>')
def ajax_stops(latitude, longitude, offset):
	loc_info = get_stops(latitude, longitude, offset)
	json = {}
	json['stops'] = loc_info[0]
	json['more'] = loc_info[-1]
	return simplejson.dumps(json)

@app.route('/stop/<stop_id>')
def stop_info(stop_id):
	
	s = get_stop(stop_id)

	# get the users location (to show on the map)
	userlat = request.args.get('userlat', '')
	userlong = request.args.get('userlong', '')

	return render_template('stop_info.html', stop=s.__dict__, userlat=userlat, userlong=userlong)

# INPUT

@app.route('/postcode/', methods=['GET', 'POST'])
def enter_location():
	if request.method == 'POST':
		postcode = request.form['postcode'].replace(" ", "")
		r = requests.get("http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % (postcode), "GET")
		try:
			d = simplejson.loads(r.text)
			latitude = d['results'][0]['geometry']['location']['lat']
			longitude = d['results'][0]['geometry']['location']['lng']
			url = "/stops/%s+%s" % (latitude, longitude)
			return redirect(url)
		except ValueError:
			return render_template('enter_postcode_again.html')
		except IndexError:
			return render_template('enter_postcode_again.html')
	else:
		return render_template('enter_postcode.html')

@app.route('/')
def get_location():
	return render_template('get_location.html')

# RUN CONFIG

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)