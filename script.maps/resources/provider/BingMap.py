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

class BingMap:
	def __init__(self, key):
		self._sizes = ['896,504', '640,360', '480,270']
		self._types = ['Road', 'Aerial', 'AerialWithLabels']
		self._minZoom = 0
		self._maxZoom = 21
		self._format = 'jpeg'
		self._key = key
		self.pan(0.000000, 0.000000).zoom(2).type(0).size(0)

	@staticmethod
	def providerInfo():
		return {'name': 'Bing', 'setting': [{'@id': 'api.bing.key', '@label': 'Bing Maps Key', '@type': 'text'}]}

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
			up = urllib.urlopen('http://dev.virtualearth.net/REST/v1/Locations?q=%sinclnb=0&maxRes=1&key=%s' % (urllib.quote_plus(address), self._key))
			response = json.load(up)
			if 'statusCode' in response:
				if response['statusCode'] == 200:
					if 'resourceSets' in response and len(response['resourceSets']) > 0 and 'estimatedTotal' in response['resourceSets'][0] and response['resourceSets'][0]['estimatedTotal'] > 0:
						info['status'] = 'OK'
						result = response['resourceSets'][0]['resources'][0]
						if 'point' in result:
							info['lat'] = result['point']['coordinates'][0]
							info['lng'] = result['point']['coordinates'][1]
						if 'name' in result:
							info['address'] = result['name']
					else:
						info['status'] = 'NO_RESULT'
				elif response['statusCode'] in [401, 403]:
					info['status'] = 'LIMIT_EXCEEDED'
				else:
					info['status'] = 'ERROR'
		except:
			info['status'] = 'ERROR'
		return info

	def url(self):
		return 'http://dev.virtualearth.net/REST/v1/Imagery/Map/%s/%.6f,%.6f/%i?ms=%s&fmt=%s&key=%s' % (self._type, self._lat, self._lng, self._zoom, self._size, self._format, self._key)
