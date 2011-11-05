from busscraper.busscraper import stop, postcode

import httplib2

try:
	import json as simplejson
except ImportError:
	try:
		import simplejson
	except ImportError:
		from django.utils import simplejson

from flask import Flask, render_template, url_for, g
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

@app.route('/postcode/<location>')
def stops_near_postcode(location):
	stops = postcode(location, "oxfordshire")
	return render_template('postcode.html', stops=stops)
	#json = simplejson.dumps(stops)
	#return json

@app.route('/get-location/')
def get_location():
	return render_template('get_location.html')

@app.route('/stops/<latitude>+<longitude>')
def stops(latitude, longitude):
	stop_list = query_db('SELECT * FROM (SELECT AtcoCode, CommonName, (((latitude - ?) * (latitude - ?)) + (longitude - (?)) * (longitude - (?))) * (110 * 110) AS dist FROM stops ORDER BY dist ASC) AS tab WHERE tab.dist <= (0.5 * 0.5);', [latitude, latitude, longitude, longitude])
	options = []
	for bus_stop in stop_list:
		atco = bus_stop["AtcoCode"]
		atco = atco[1:-1]
		buses = stop(atco, "oxfordshire")
		name = bus_stop["CommonName"]
		name = name[1:-1]
		buses.append(name)
		distance = bus_stop["dist"]
		distance = distance * 1000
		distance = int(distance)
		buses.append(distance)
		options.append(buses)
	#json = simplejson.dumps(options)
	#return json
	return render_template('stop_list.html', stop_list=options)

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run(debug=True)
