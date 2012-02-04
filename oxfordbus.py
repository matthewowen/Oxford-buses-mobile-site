from busscraper import stop, postcode

import httplib2

try:
	import json as simplejson
except ImportError:
	try:
		import simplejson
	except ImportError:
		from django.utils import simplejson

from flask import Flask, render_template, url_for, g, redirect, request
import sqlite3

app = Flask(__name__)

DATABASE = 'stopsdb'

def connect_db():
    return sqlite3.connect(DATABASE)

def get_stops(latitude, longitude, offset):
	# get the nearby stops from the database
	stop_list = query_db('SELECT * FROM (SELECT AtcoCode, CommonName, Landmark, (((latitude - ?) * (latitude - ?)) + (longitude - (?)) * (longitude - (?))) * (110 * 110) AS dist FROM stops ORDER BY dist ASC) AS tab WHERE tab.dist <= (2 * 2);', [latitude, latitude, longitude, longitude])
	"""
	use the offset to figure out which stops in the list we're interested in.
	if the list has more stops beyond those we're using, set the more variable to be true
	"""
	length = len(stop_list)
	u = offset + 10
	if length > u:
		more = True
	else:
		more = False
	stop_list = stop_list[offset:u]
	# run through the new stop list getting the info for each one
	options = []
	for bus_stop in stop_list:
		atco = bus_stop["AtcoCode"]
		buses = stop(atco, "oxfordshire")[:10]
		name = bus_stop["CommonName"]
		landmark = bus_stop["Landmark"]
		if name == landmark:
			pass
		else:
			names = [name, landmark]
			name = " ".join(names)
		distance = bus_stop["dist"]
		distance = distance * 1000
		distance = int(distance)
		stop_details = {'name': name, 'distance': distance, 'buses': buses}
		options.append(stop_details)
	# return a tuple containing the list of stop options, and whether or not there are more stops
	return (options, more)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route('/postcode/', methods=['GET', 'POST'])
def enter_location():
	if request.method == 'POST':
		postcode = request.form['postcode']
		postcode = postcode.replace(" ", "")
		http = httplib2.Http()
		resp, content = http.request("http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % (postcode), "GET")
		try:
			content2 = simplejson.loads(content)
			results = content2['results']
			results = results[0]
			geometry = results['geometry']
			location = geometry['location']
			latitude = location['lat']
			longitude = location['lng']
			url = "/stops/%s+%s" % (latitude, longitude)
			return redirect(url)
		except ValueError:
			return render_template('enter_postcode_again.html')
		except IndexError:
			return render_template('enter_postcode_again.html')
	else:
		return render_template('enter_postcode.html')

@app.route('/no-location')
def no_location():
	return render_template('no_location.html')

@app.route('/')
def get_location():
	return render_template('get_location.html')

@app.route('/stops/<latitude>+<longitude>')
def stops(latitude, longitude):
	loc_info = get_stops(latitude, longitude, 0)
	options = loc_info[0]
	more = loc_info[-1]
	return render_template('stop_list.html', stop_list=options, more=more)

@app.route('/ajax/stops/<latitude>+<longitude>/<int:offset>')
def ajax_stops(latitude, longitude, offset):
	loc_info = get_stops(latitude, longitude, offset)
	json = {}
	json['stops'] = loc_info[0]
	json['more'] = loc_info[-1]
	return simplejson.dumps(json)

@app.route('/about')
def about():
	return render_template('about.html')

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	return render_template('500.html'), 500

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
