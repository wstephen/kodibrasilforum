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

class MapQuest:
	def __init__(self, key):
		self._sizes = ['1280,720', '640,360', '480,270']
		self._types = ['map', 'sat', 'hyb']
		self._minZoom = 0
		self._maxZoom = 18
		self._format = 'jpg'
		self._key = key
		self.pan(0.000000, 0.000000).zoom(2).type(0).size(0)

	@staticmethod
	def providerInfo():
		return {'name': 'MapQuest', 'setting': [{'@id': 'api.mapquest.key', '@label': 'MapQuest AppKey', '@type': 'text'}]}

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

	def url(self):
		return 'http://open.mapquestapi.com/staticmap/v4/getmap?center=%.6f,%.6f&zoom=%i&type=%s&size=%s&imagetype=%s&key=%s' % (self._lat, self._lng, self._zoom, self._type, self._size, self._format, self._key)
