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

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'provider'))
import xbmcgui, re, urllib, urlparse, shutil, pkgutil
import kodifu


addon = kodifu.Addon()
__ = addon.str


class Map:
	def __init__(self):
		self._reLatLon = re.compile('^\s*\d+\.\d+\s*,\s*\d+\.\d+\s*$')
                self._loadProviders()
                self._info = {'lat': 0.0, 'lng': 0.0}
		self._steps = [0, 0, 8.000000, 6.000000, 4.000000, 3.000000, 2.000000, 1.000000, 0.500000, 0.200000, 0.100000, 0.050000, 0.020000, 0.010000, 0.005000, 0.002000, 0.001000, 0.000500, 0.000200, 0.000100, 0.000050, 0.000020]
                self._zoom = 2
                self._step = self._steps[self._zoom]
                self._lat = 0.000000
                self._lng = 0.000000
		self._heading = 0
		self._pitch = 0
		# Not possible currently (future-proof)
		self._direction = None

        def _loadProviders(self):
            mod_path = os.path.join(os.path.dirname(__file__), 'resources', 'provider')
            modules = pkgutil.iter_modules(path=[mod_path])

            addon.settings.mutate.remove(2, 0, -1)
            self._mapProviders = {}
            self._geocodingProviders = {}
            self._placesProviders = {}
            self._panoramaProviders = {}
            mapValues = []
            geocodingValues = []
            placesValues = []
            panoramaValues = []
            for loader, mod_name, ispkg in modules: 
                if mod_name not in sys.modules:
                    loaded_mod = __import__("resources.provider."+mod_name, fromlist=[mod_name])
                    loaded_class = getattr(loaded_mod, mod_name)
                    info = loaded_class.providerInfo()
                    args = []
                    for arg in info['setting']:
                        args.append(addon.settings.get(arg['@id']))
                    instance = loaded_class(*args)
                    if hasattr(instance, 'url'):
                        self._mapProviders[info['name']] = instance
                        mapValues.append(info['name'])
                    if hasattr(instance, 'geocode'):
                        self._geocodingProviders[info['name']] = instance
                        geocodingValues.append(info['name'])
                    if hasattr(instance, 'places'):
                        self._placesProviders[info['name']] = instance
                        placesValues.append(info['name'])
                    if hasattr(instance, 'panorama'):
                        self._panoramaProviders[info['name']] = instance
                        panoramaValues.append(info['name'])
                    addon.settings.mutate.add(2, -1, info['setting'])
            addon.settings.mutate.remove(0, 0, 1).add(0, 0, {'@label': '32810', '@type': 'labelenum', '@id': 'map.provider', '@default': 'Google', '@values': '|'.join(mapValues)})
            addon.settings.mutate.remove(0, 1, 2).add(0, 1, {'@label': '32811', '@type': 'labelenum', '@id': 'geocoding.provider', '@default': 'Google', '@values': '|'.join(geocodingValues)})
            addon.settings.mutate.remove(0, 2, 3).add(0, 2, {'@label': '32812', '@type': 'labelenum', '@id': 'places.provider', '@default': 'Foursquare', '@values': '|'.join(placesValues)})
            addon.settings.mutate.remove(0, 3, 4).add(0, 3, {'@label': '32813', '@type': 'labelenum', '@id': 'panorama.provider', '@default': 'Google', '@values': '|'.join(panoramaValues)})
            addon.settings.mutate.save()
                

	def mapProvider(self, provider):
		if not provider in self._mapProviders:
			provider = 'Google'
		self._map = self._mapProviders[provider]
		return self

	def geocodingProvider(self, provider):
		if not provider in self._geocodingProviders:
			provider = 'Google'
		self._geocoder = self._geocodingProviders[provider]
		return self

        def placesProvider(self, provider):
		if not provider in self._placesProviders:
			provider = 'Foursquare'
		self._places = self._placesProviders[provider]
		return self

        def panoramaProvider(self, provider):
		if not provider in self._panoramaProviders:
			provider = 'Google'
		self._panorama = self._panoramaProviders[provider]
		return self
		
	def size(self, value):
		self._map.size(value)
		return self

	def type(self, value):
		self._map.type(value)
		return self

	def pan(self, arg1, arg2=1):
		if arg1 == 'down':
			self._lat -= self._step * arg2
		elif arg1 == 'up':
			self._lat += self._step * arg2
		elif arg1 == 'left':
			self._lng -= self._step * arg2
		elif arg1 == 'right':
			self._lng += self._step * arg2
		elif isinstance(arg1, float) and isinstance(arg2, float):
			self._lat = arg1
			self._lng = arg2
		self._lat = min(90, max(-90, self._lat))
		self._lng = min(180, max(-180, self._lng))
                self._map.pan(self._lat, self._lng)
		return self

	def zoom(self, value):
		if value == 'in':
			self._zoom += 1
		elif value == 'out':
			self._zoom -= 1
		elif isinstance(value, int):
			self._zoom = value
		self._zoom = min(21, max(self._zoom, 0))
		self._step = self._steps[self._zoom]
                self._map.zoom(self._zoom)
		return self

	def geocode(self, address):
		return self._geocoder.geocode(address)

	def places(self, query):
		return self._places.places(self._lat, self._lng, query)

	def url(self):
		return self._map.url()

	def look(self, arg1, arg2=None):
		if arg1 == 'left':
			self._heading -= 30
		elif arg1 == 'right':
			self._heading += 30
		elif arg1 == 'up':
			self._pitch += 15
		elif arg1 == 'down':
			self._pitch -= 15
		elif isinstance(arg1, int):
			self._heading = arg1
		elif arg2 and isinstance(arg2, int):
			self._pitch = arg2
		self._heading = (self._heading + 3600) % 360
		self._pitch = max(min(self._pitch, 90), -90)
		self._panorama.look(self._heading, self._pitch)
		return self

	# not possible currently with any panorama provider
	# kept to be future-proof (once it becomes possible)
	# the new lat/lng will be decided by the wak method in the provider
	# if not possible to move, then None is returned, and nothing change
	def move(self, direction):
		info = self._panorama.move(self._direction)
		if info:
			self._lat = info['lat']
			self._lng = info['lng']
		return self

	def panorama(self):
		return self._panorama.panorama()

	def goto(self, address):
		if self._reLatLon.match(address):
			address = address.strip()
			self._lat = float(address.split(',')[0].strip())
			self._lng = float(address.split(',')[1].strip())

		else:
			info = self.geocode(address)
                        if info['status'] == 'OK':
                            self._lat = info['lat']
                            self._lng = info['lng']
                        elif info['status'] == 'NO_RESULT':
                                addon.dialog.ok(32700, 32701)
                        elif info['status'] == 'LIMIT_EXCEEDED':
                                addon.dialog.ok(32702, 32703)
                        else:
                                addon.dialog.ok(32704, 32705)
	        self._map.pan(self._lat, self._lng)
		return self

        def get(self, id):
                if id == 'lat':
                        return self._lat
                elif id == 'lng':
                        return self._lng
                elif id == 'zoom':
                        return self._zoom


class MapWindow(addon.window):
	#def __new__(cls, *args):
	#	return super(MapWindow, cls).__new__(cls, *args)

	def __init__(self, *args):
		super(addon.window, self).__init__(*args)
		self.onInit()

	def onInit(self):
		self.setCoordinateResolution(0)

                self._mapProvider = addon.settings.get('map.provider')
                self._geocodingProvider = addon.settings.get('geocoding.provider')
                self._placesProvider = addon.settings.get('places.provider')
                self._panoramaProvider = addon.settings.get('panorama.provider')
		self._cache = addon.settings.get('map.cache') == 'true'
		self._mapsCacheTimeout = addon.settings.get('map.cache.timeout', int)
		self._rememberLocation = addon.settings.get('location.remember') == 'true'
		self._quality = addon.settings.get('map.quality', int)
		self._type = addon.settings.get('map.type', int)
		self._zoom = addon.settings.get('map.zoom', int)

                if self._rememberLocation:
                    self._lat = addon.settings.get('location.lat', float)
                    self._lng = addon.settings.get('location.lng', float)
                    #self._zoom = addon.settings.get('location.zoom', int)
                    self._address = '%.6f,%.6f' % (self._lat, self._lng)
                else:
                    self._address = addon.settings.get('map.home')

		self._map = Map()
		self._map.mapProvider(self._mapProvider).geocodingProvider(self._geocodingProvider).placesProvider(self._placesProvider).panoramaProvider(self._panoramaProvider)
		self._map.size(self._quality).type(self._type).zoom(self._zoom).goto(self._address)

		self._url = ''

                _tbColor = addon.dir('skin', 'Default', 'media', 'transparent-black.png')
                _bColor = addon.dir('skin', 'Default', 'media', 'blue.png')
                _nColor = addon.dir('skin', 'Default', 'media', 'navy.png')
                _wColor = addon.dir('skin', 'Default', 'media', 'white.png')

		self._backImg = xbmcgui.ControlImage(0, 0, 1920, 1080, self._url) 
		self._mapImg = xbmcgui.ControlImage(0, 0, 1920, 1080, self._url) 
		self._overlayImg = xbmcgui.ControlImage(0, 0, 1920, 1080, _tbColor) 
		self._searchEdt = xbmcgui.ControlButton(20, 20, 700, 70, __(32001), _wColor, _wColor, textColor='0x99000000', focusedColor='0x99000000')
		self._searchBtn = xbmcgui.ControlButton(720, 20, 160, 70, __(32002), _nColor, _bColor, alignment=0x00000002|0x00000004, textColor='0xFFFFFFFF', focusedColor='0xFFFFFFFF')
		self._homeBtn = xbmcgui.ControlButton(900, 20, 160, 70, __(32003), _nColor, _bColor, alignment=0x00000002|0x00000004, textColor='0xFFFFFFFF', focusedColor='0xFFFFFFFF')
		self._placesBtn = xbmcgui.ControlButton(1063, 20, 160, 70, __(32004), _nColor, _bColor, alignment=0x00000002|0x00000004, textColor='0xFFFFFFFF', focusedColor='0xFFFFFFFF')
		self._panoramaBtn = xbmcgui.ControlButton(1226, 20, 180, 70, __(32005), _nColor, _bColor, alignment=0x00000002|0x00000004, textColor='0xFFFFFFFF', focusedColor='0xFFFFFFFF')
		self.addControl(self._backImg)
		self.addControl(self._mapImg)
		self.addControl(self._overlayImg)
		self.addControl(self._searchEdt)
		self.addControl(self._searchBtn)
		self.addControl(self._homeBtn)
		self.addControl(self._placesBtn)
		self.addControl(self._panoramaBtn)
                self._overlayImg.setVisible(False)
		self._searchBtn.setNavigation(self._searchBtn, self._searchBtn, self._searchBtn, self._homeBtn)
		self._homeBtn.setNavigation(self._homeBtn, self._homeBtn, self._searchBtn, self._placesBtn)
		self._placesBtn.setNavigation(self._placesBtn, self._placesBtn, self._homeBtn, self._panoramaBtn)
		self._panoramaBtn.setNavigation(self._panoramaBtn, self._panoramaBtn, self._placesBtn, self._panoramaBtn)
		self.setFocus(self._searchBtn)
		self.toggleControls(False)
		self._panoramaMode = False
                self.update()

	def update(self):
		if self._panoramaMode:
			url = self._map.panorama()
			if not url:
			    addon.dialog.ok(32709, 32710)
			elif self._url != url:
				self._backImg.setImage(self._url, False)
				self._url = url
				if self._cache:
				    cache = addon.dir('data', 'cache', 'panoramas', self._panoramaProvider)
				    if not addon.vfs.exists(cache):
					    addon.vfs.mkdirs(cache)
				    filename = addon.dir('data', 'cache', 'panoramas', self._panoramaProvider, urlparse.urlparse(self._url).query)
				    if not addon.vfs.exists(filename):
					urllib.urlretrieve(self._url, filename)
				    self._url = filename
				self._mapImg.setImage(self._url, False)
		else:
			url = self._map.url()
			if self._url != url:
				lat = self._map._lat
				lng = self._map._lng
				self._searchEdt.setLabel('%f,%f' % (lat, lng))
				self._backImg.setImage(self._url, False)
				self._url = url
				if self._cache:
				    cache = addon.dir('data', 'cache', 'maps', self._mapProvider)
				    if not addon.vfs.exists(cache):
					    addon.vfs.mkdirs(cache)
				    filename = addon.dir('data', 'cache', 'maps', self._mapProvider, urlparse.urlparse(self._url).query)
				    if not addon.vfs.exists(filename):
					urllib.urlretrieve(self._url, filename)
				    self._url = filename
				self._mapImg.setImage(self._url, False)

        def nextType(self):
                self._type = (self._type + 1) % 3
                self._map.type(self._type)

        def toggleControls(self, state=None):
                if state == None:
                        self._visible = not self._visible
                else:
                        self._visible = state
                self._searchEdt.setVisible(self._visible)
                self._searchBtn.setVisible(self._visible)
                self._homeBtn.setVisible(self._visible)
                self._placesBtn.setVisible(self._visible)
                self._panoramaBtn.setVisible(self._visible)
                if self._visible:
                        self.setFocus(self._searchBtn)
        
        def onClick(self, controlId):
                pass

        def onDoubleClick(self, controlId):
                pass

        def onControl(self, control):
                if control == self._searchBtn:
                    self._overlayImg.setVisible(True)
                    self._address = addon.dialog.input('')
                    if self._address:
                        self._map.goto(self._address)
                        self.update()
                    self._overlayImg.setVisible(False)
                elif control == self._homeBtn:
                    self._address = addon.settings.get('map.home')
                    self._map.goto(self._address)
                    self.update()
                elif control == self._placesBtn:
                    self._overlayImg.setVisible(True)
		    query = addon.dialog.input(32708)
		    if query:
			    info = self._map.places(query)
			    pls = []
			    if info['status'] == 'OK':
				    for i in info['places']:
					pls.append('%s (%.4f,%.4f)' % (i['name'], i['lat'], i['lng']))
				    i = addon.dialog.select(32004, pls)
				    if i > -1:
					self._map.pan(info['places'][i]['lat'],info['places'][i]['lng'])
					self.update()
			    elif info['status'] == 'NO_RESULT':
				    addon.dialog.ok(32700, 32701)
			    elif info['status'] == 'LIMIT_EXCEEDED':
				    addon.dialog.ok(32702, 32703)
			    else:
				    addon.dialog.ok(32704, 32705)
                    self._overlayImg.setVisible(False)
                elif control == self._panoramaBtn:
			self._panoramaMode = True
			self._map.look(0, 0)
			self._url = ''
			self.toggleControls(False)
			self.update()

	def onAction(self, action):
		if action in [xbmcgui.ACTION_PREVIOUS_MENU, xbmcgui.ACTION_NAV_BACK]:
			if self._panoramaMode:
			    self._panoramaMode = False
			    self._url = ''
			    self.toggleControls(False)
			    self.update()
                        elif self._visible:
                            self.toggleControls(False)
                        else:
                            addon.settings.set('location.lat', self._map.get('lat'))
                            addon.settings.set('location.lng', self._map.get('lng'))
                            addon.settings.set('location.zoom', self._map.get('zoom'))
                            if self._mapsCacheTimeout == 1:
                                clearMapsCache()
                            self.close()

		if action in [xbmcgui.ACTION_CONTEXT_MENU, xbmcgui.KEY_BUTTON_X]:
                        self.toggleControls()

                if self._visible:
			if action == xbmcgui.ACTION_MOVE_DOWN:
                                self.toggleControls(False)
			elif action in [xbmcgui.ACTION_PAGE_DOWN, xbmcgui.ACTION_CHANNEL_DOWN, xbmcgui.KEY_BUTTON_RIGHT_THUMB_BUTTON]:
				self._map.zoom('out')
				self.update()
			elif action in [xbmcgui.ACTION_PAGE_UP, xbmcgui.ACTION_CHANNEL_UP, xbmcgui.KEY_BUTTON_RIGHT_TRIGGER]:
				self._map.zoom('in')
				self.update()
                elif self._panoramaMode:
			if action == xbmcgui.ACTION_MOVE_DOWN:
				self._map.look('down')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_UP:
				self._map.look('up')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_LEFT:
				self._map.look('left')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_RIGHT:
				self._map.look('right')
				self.update()
			# moving doesn't work (not possible)
			# kept to be future-proof (once it becomes possible)
			# see Map and GoogleMap move method comments
			elif action in [xbmcgui.ACTION_PAGE_DOWN, xbmcgui.ACTION_CHANNEL_DOWN, xbmcgui.KEY_BUTTON_RIGHT_THUMB_BUTTON]:
				self._map.move('forward')
				self.update()
			elif action in [xbmcgui.ACTION_PAGE_UP, xbmcgui.ACTION_CHANNEL_UP, xbmcgui.KEY_BUTTON_RIGHT_TRIGGER]:
				self._map.move('backward')
				self.update()
		else:
			if action == xbmcgui.ACTION_MOVE_DOWN:
				self._map.pan('down')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_UP:
				self._map.pan('up')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_LEFT:
				self._map.pan('left')
				self.update()
			elif action == xbmcgui.ACTION_MOVE_RIGHT:
				self._map.pan('right')
				self.update()
			elif action in [xbmcgui.ACTION_PAGE_DOWN, xbmcgui.ACTION_CHANNEL_DOWN, xbmcgui.KEY_BUTTON_RIGHT_THUMB_BUTTON]:
				self._map.zoom('out')
				self.update()
			elif action in [xbmcgui.ACTION_PAGE_UP, xbmcgui.ACTION_CHANNEL_UP, xbmcgui.KEY_BUTTON_RIGHT_TRIGGER]:
				self._map.zoom('in')
				self.update()

                if action in [xbmcgui.ACTION_SHOW_INFO, xbmcgui.KEY_BUTTON_Y]:
                        self.nextType()
                        self.update()

	def onFocus(self, id):
		pass


@addon.path()
def main():
    mapWindow = MapWindow()
    mapWindow.doModal()
    del mapWindow


@addon.path()
def clearMapsCacheAction():
        clearMapsCache()
        addon.dialog.notification(32706, 32707)

def clearMapsCache():
        if addon.vfs.exists(addon.dir('data', 'cache', 'maps')):
            shutil.rmtree(addon.dir('data', 'cache', 'maps'))


addon.end()
