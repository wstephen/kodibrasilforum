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

class Foursquare:
	def __init__(self, id, secret=None):
		self._id = id
		self._secret = secret

	@staticmethod
	def providerInfo():
		return {'name': 'Foursquare', 'setting': [{'@id': 'api.foursquare.id', '@label': 'Foursquare API Client ID', '@type': 'text'}, {'@id': 'api.foursquare.secret', '@label': 'Foursquare API Client Secret', '@type': 'text'}]}

	def places(self, lat, lng, query):
		url = 'https://api.foursquare.com/v2/venues/search?ll=%.6f,%.6f&query=%s&limit=50&client_id=%s&client_secret=%s&v=20130815' % (lat, lng, query, self._id, self._secret)
		print url
		up = urllib.urlopen(url)
		response = json.load(up)
		info = {'places': []}
		try:
			if response and 'meta' in response:
				if response['meta']['code'] == 200:
					info['status'] = 'OK'
					for v in response['response']['venues']:
						p = {'id': v['id'], 'name': v['name'], 'lat': v['location']['lat'], 'lng': v['location']['lng'], 'distance': v['location']['distance'], 'comments': v['stats']['tipCount'], 'visited': v['stats']['usersCount']}
						if 'formattedAddress' in v['location']:
							p['address'] = ', '.join(filter(None, v['location']['formattedAddress']))
						if 'phone' in v['contact']:
							p['phone'] = v['contact']['phone']
						if 'twitter' in v['contact']:
							p['phone'] = v['contact']['twitter']
						info['places'].append(p)
				elif response['meta']['code'] == 400:
					info['status'] = 'LIMIT_EXCEEDED'
				else:
					info['status'] = 'ERROR'
			else:
				info['status'] = 'ERROR'
		except:
			info['status'] = 'ERROR'
		return info
		
