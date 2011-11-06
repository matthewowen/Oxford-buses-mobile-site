from busscraper.busscraper import stop, postcode

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
	stop_list = query_db('SELECT * FROM (SELECT AtcoCode, CommonName, Landmark, (((latitude - ?) * (latitude - ?)) + (longitude - (?)) * (longitude - (?))) * (110 * 110) AS dist FROM stops ORDER BY dist ASC) AS tab WHERE tab.dist <= (0.75 * 0.75);', [latitude, latitude, longitude, longitude])
	options = []
	for bus_stop in stop_list:
		atco = bus_stop["AtcoCode"]
		atco = atco[1:-1]
		buses = stop(atco, "oxfordshire")
		name = bus_stop["CommonName"]
		name = name[1:-1]
		landmark = bus_stop["Landmark"]
		landmark = landmark[1:-1]
		if name == landmark:
			pass
		else:
			names = [name, landmark]
			name = " ".join(names)
		#buses.append(name)
		distance = bus_stop["dist"]
		distance = distance * 1000
		distance = int(distance)
		stop_details = {'name': name, 'distance': distance, 'buses': buses}
		#buses.append(distance)
		options.append(stop_details)
	return render_template('stop_list.html', stop_list=options)

@app.route('/about')
def about():
	return render_template('about.html')

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run()
