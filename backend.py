from flask import Flask, render_template, url_for, g, redirect, request
import httplib2, redis, sqlite3
from busscraper import stop, postcode

app = Flask(__name__)

DATABASE = 'stopsdb'

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def connect_db():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

class BusStop(object):

	def retrieve_scraper(self):
		"""
		retrieve buses using busscraper.stop
		add those buses to redis for next time
		"""	
		# scrape the info - just take the first ten buses
		buses = stop(self.atco, "oxfordshire")[:10]
		
		# record data about each bus in redis
		for bus in buses:
			# increment the id counter so that the bus has a unique id
			k = r.incr('bus.id')
			# set keys for the info we've retrieved
			r.set('bus:%d:service' % (k), bus['service'])
			r.set('bus:%d:destination' % (k), bus['destination'])
			r.set('bus:%d:minutes_to_departure' % (k), bus['minutes_to_departure'])
			# put the id for the bus in this stops list of coming buses
			r.lpush(self.atco, k)
		
		# set the key to expire in a minute
		r.expire(self.atco, 60)

		return buses

	def retrieve_redis(self):
		"""
		retrieve a list of buses from redis for an atco list that is known to exist.
		takes an atco number (id of the list)
		returns a python list (same format as busscraper.stop returns)
		"""

		# create a python list for the buses
		buses = []
		# figure out how long the redis list is
		i = r.llen(self.atco)

		# go through each item in the redis list
		for l in range(i):
			# get the id of the bus
			v = r.lindex(self.atco, l)
			# start a dictionary for the values
			bus = {}
			# grab the info and put it in the dictionary
			bus['service'] = r.get('bus:%s:service' % (v))
			bus['destination'] = r.get('bus:%s:destination' % (v))
			bus['minutes_to_departure'] = int(r.get('bus:%s:minutes_to_departure' % (v)))
			# stick it on the list
			buses.append(bus)

		# list is wrong way round so reverse it
		buses.reverse()

		return buses

	def retrieve_buses(self):
		"""
		check if there's a currently cached set of buses in redis.
			if so, return said buses in a list, most recent first.
			if not, get the data using busscraper.stop, and put the data in redis
		return the buses for the stop in a list, soonest first
		"""
		# if there's a list for this stop in redis, use it
		if r.exists(self.atco):
			buses = self.retrieve_redis()

		# if we've not already got it in redis, go and get the stop info from oxontime and put it in redis
		else:
			buses = self.retrieve_scraper()

		# get rid of yucky stuff
		for bus in buses:
			bus['service'] = bus['service'].replace("&nbsp;", "")
			bus['destination'] = bus['destination'].replace("&nbsp;", "")

		return buses

	def __init__(self, atco, **kwargs):
		self.atco = atco
		self.buses = self.retrieve_buses()
		if 'name' in kwargs:
			self.name = kwargs['name']
		if 'distance' in kwargs:
			self.distance = kwargs['distance']
		if 'latitude' in kwargs:
			self.latitude = kwargs['latitude']
		if 'longitude' in kwargs:
			self.longitude = kwargs['longitude']

def name_joiner(bus_stop):
	"""
	passed a bus stop, returns a sensible name for it based on common name and landmark
	"""
	if bus_stop["CommonName"] == bus_stop["Landmark"]:
			name = bus_stop["CommonName"]
	else:
		names = [bus_stop["CommonName"], bus_stop["Landmark"]]
		name = " ".join(names)

	return name

def get_stops(latitude, longitude, offset):
	"""
	for a given latitude, longitude and offset (n):
		return a list of stops (starting with the nth nearest):
			for each stop:
				give info about the stop
				list the next ten buses at the stop
		return whether or not there are more stops nearby
	"""

	# get the nearby stops from the database
	stop_list = query_db('SELECT * FROM (SELECT AtcoCode, CommonName, Landmark, (((latitude - ?) * (latitude - ?)) + (longitude - (?)) * (longitude - (?))) * (110 * 110) AS dist FROM stops ORDER BY dist ASC) AS tab WHERE tab.dist <= (1 * 1);', [latitude, latitude, longitude, longitude])

	# use the offset to figure out which stops in the list we're interested in.
	# if the list has more stops beyond those we're using, set the more variable to be true
	if len(stop_list) > offset+10:
		more = True
	else:
		more = False
	stop_list = stop_list[offset:offset+10]

	# a list for the stops and their info
	options = []

	# run through all the stops, getting info and adding to the list
	for bus_stop in stop_list:
		# distance isn't strictly accurate, but it is near enough
		v = BusStop(bus_stop["AtcoCode"], name=name_joiner(bus_stop), distance=int(bus_stop["dist"] * 1000))

		options.append(v.__dict__)
	
	# return a tuple containing the list of stop options, and whether or not there are more stops
	return (options, more)

def get_stop(stop_id):
	"""
	get the information about a particular stop, given a stop_id (atco)
	"""

	bus_stop = query_db('SELECT * FROM stops WHERE AtcoCode = ?;', [stop_id])[0]

	return BusStop(bus_stop["AtcoCode"], name=name_joiner(bus_stop), latitude=bus_stop['Latitude'], longitude=bus_stop['Longitude'])