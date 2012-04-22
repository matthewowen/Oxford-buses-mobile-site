import requests
from BeautifulSoup import BeautifulSoup

def get_content(URL):
	"""
	Pass a URL. Get back some Beautiful Soup.
	"""

	r = requests.get(URL)
	soup = BeautifulSoup(r.text)

	return soup

def parse_soup(soup):
	"""
	parses the soup we get from get_buses
	"""

	stopTable = soup.findAll('table')[1]
	stopBody = stopTable.find('tbody')
	if not stopBody:
		return []

	rows = stopBody.findAll('tr')

	bus_list = []

	for row in rows:
		d = {}
		cells = row.findAll('td')

		d['service'] = cells[0].string
		d['destination'] = cells[1].string.replace('&amp;', '&')
		d['minutes_to_departure'] = cells[2].string.replace(' mins', '')

		bus_list.append(d)

	return bus_list

class stop(object):
	"""
	init with a stop id
	get back buses for that stop as a list of dictionaries
	"""

	def get_buses(self):
		url = 'http://www.oxontime.com/Naptan.aspx?t=departure&sa=%s&format=xhtml' % (self.id)

		soup = get_content(url)

		self.bus_list = parse_soup(soup)

	def __init__(self, id):
		self.id = id

		self.get_buses()