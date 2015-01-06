#
#     Copyright (C) 2014 A. Alsaleh [a.a.alsaleh at gmail dot com]
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import urllib, json

class GoogleMap:
	def __init__(self, key):
		self._sizes = ['640x360&scale=2', '640x360&scale=1', '480x270&scale=1']
		self._types = ['roadmap', 'satellite', 'hybrid']
		self._minZoom = 0
		self._maxZoom = 21
		self._format = 'jpg'
		self._key = key
		self.pan(0.000000, 0.000000).zoom(2).type(0).size(0).look(0, 0)

	@staticmethod
	def providerInfo():
		return {'name': 'Google', 'setting': [{'@id': 'api.google.key', '@label': 'Google Public API Key', '@type': 'text'}]}

	def size(self, value):
		self._size = self._sizes[value]
		return self
	
	def type(self, value):
		self._type = self._types[value]
		return self

	def pan(self, lat, lng):
		self._lat = lat
		self._lng = lng
		return self

	def zoom(self, value):
		self._zoom = min(self._maxZoom, max(value, self._minZoom))
		return self

	def geocode(self, address):
		info = {}
		try:
			up = urllib.urlopen('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (urllib.quote_plus(address), self._key))
			response = json.load(up)
			if 'status' in response:
				if response['status'] == 'OK':
					info['status'] = 'OK'
					if 'results' in response and len(response['results']) > 0:
						result = response['results'][0]
						if 'geometry' in result:
							info['lat'] = result['geometry']['location']['lat']
							info['lng'] = result['geometry']['location']['lng']
						if 'formatted_address' in result:
							info['address'] = result['formatted_address']
				elif response['status'] == 'ZERO_RESULTS':
					info['status'] = 'NO_RESULT'
				elif response['status'] == 'OVER_QUERY_LIMIT':
					info['status'] = 'LIMIT_EXCEEDED'
				else:
					info['status'] = 'ERROR'
		except:
			info['status'] = 'ERROR'
		return info

	def look(self, heading, pitch):
		self._heading = heading
		self._pitch = pitch
		return self

	# moving is not possible with Google Street View Image API (Static/HTTP)
	# kept to be future-proof (once it becomes possible)
	# must move 'backward' or 'forward' (based on current heading and lat/lng)
	# must return the new 'lat'/'lng' (and 'address' if possible) as dict if the move was successfull
	# otherwise return None
	def move(self, direction):
		self._direction = direction
		return None

	# should return None if no panorama, but this is not possible with Google Street View Image API (static/HTTP)
	def panorama(self):
		if self._key:
			return 'http://maps.googleapis.com/maps/api/streetview?location=%.6f,%.6f&heading=%i&fov=%i&pitch=%i&size=%s&key=%s' % (self._lat, self._lng, self._heading, 90, self._pitch, '640x360', self._key)
		else:
			return 'http://maps.googleapis.com/maps/api/streetview?location=%.6f,%.6f&heading=%i&fov=%i&pitch=%i&size=%s' % (self._lat, self._lng, self._heading, 90, self._pitch, '640x360')

	def url(self):
		if self._key:
			return 'http://maps.googleapis.com/maps/api/staticmap?center=%.6f,%.6f&zoom=%i&maptype=%s&size=%s&format=%s&key=%s' % (self._lat, self._lng, self._zoom, self._type, self._size, self._format, self._key)
		else:
			return 'http://maps.googleapis.com/maps/api/staticmap?center=%.6f,%.6f&zoom=%i&maptype=%s&size=%s&format=%s' % (self._lat, self._lng, self._zoom, self._type, self._size, self._format)
