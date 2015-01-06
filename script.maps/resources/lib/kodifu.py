#
#    Kodi Fu
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

import sys, os, re, urllib, json, time, urlparse, datetime, inspect, traceback
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs
import xmltodict

class Addon:
	def __init__(self, id=None, debug=False):
		if id:
			self._addon = xbmcaddon.Addon(id=id)
		else:
			try:
				self._addon = xbmcaddon.Addon()
			except:
				self._addon = xbmcaddon.Addon(os.path.split(os.path.dirname(sys.argv[0]))[1])
		self._dir = {
			'path': xbmc.translatePath(self._addon.getAddonInfo('path')).decode("utf-8"),
			'data': xbmc.translatePath(self._addon.getAddonInfo('profile')).decode("utf-8"),
			'skin': xbmc.translatePath(os.path.join(self._addon.getAddonInfo('path'), 'resources', 'skins')).decode("utf-8"),
			'xbmc.skin': xbmc.translatePath('special://skin').decode("utf-8")
		}
		self._id = self._addon.getAddonInfo('id')

		self._routes = {}
		self._match = None
		if self._id.find('plugin.') == 0:
			self._plugin = True
			self._url = urlparse.urlparse(sys.argv[0]).path
			self._urlFunc = self._url.split('/')[-1]
			if self._urlFunc == '':
				self._urlFunc = 'main'
			self._urlArgs = urlparse.parse_qs(urlparse.urlparse(sys.argv[2]).query)
			self._urlVarsRE = re.compile(r'\{\{([a-zA-Z0-9_\-]+)\}\}')
		elif self._id.find('script.') == 0:
			self._plugin = False
			self._urlFunc = 'main'
			self._urlArgs = {}
			if len(sys.argv) >= 2:
				self._urlFunc = sys.argv[1]
				if len(sys.argv) > 2:
					self._urlArgs = urlparse.parse_qs(sys.argv[2])

		self._debug = debug
		if self._debug:
			self._log = xbmcvfs.File(os.path.join(self._dir['data'], 'addon.log'))
			_log = self._log.read()
			self._log = xbmcvfs.File(os.path.join(self._dir['data'], 'addon.log'), 'w')
			self._log.write(_log)

		self._handler = {'*': []}
		self._settings = None
		self._directory = None
		self._storage = None
		self._dialog = None
		self._vfs = None
		self._player = None
		self._monitor = None
		self.window = AddonWindow

	@property
	def settings(self):
		if not self._settings:
			self._settings = AddonSettings(self._id, self._addon)
		return self._settings

	@property
	def directory(self):
		if not self._directory:
			self._directory = AddonDirectory(self._addon)
		return self._directory

	@property
	def storage(self):
		if not self._storage:
			self._storage = AddonStorage(self._addon)
		return self._storage

	@property
	def dialog(self):
		if not self._dialog:
			self._dialog = AddonDialog(self._addon)
		return self._dialog

	@property
	def vfs(self):
		if not self._vfs:
			self._vfs = AddonVirtualFileSystem()
		return self._vfs

	@property
	def player(self):
		if not self._player:
			self._player = AddonPlayer()
			self._player._setTriggerer(self.trigger)
		return self._player

	@property
	def monitor(self):
		if not self._monitor:
			self._monitor = AddonMonitor()
			self._monitor._setTriggerer(self.trigger)
		return self._monitor

	def on(self, event, callback):
		event = event.lower()
		if not event in self._handler:
			self._handler[event] = []
		self._handler[event].append(callback)
		return self

	def off(self, event, callback=None):
		event = event.lower()
		if event in self._handler:
			if callback:
				self._handler[event][:] = [cb for cb in self._handler[event] if callback == cb]
			else:
				del self._handler[event]
		return self

	def trigger(self, event, eventData={}):
		event = event.lower()
		eventData['name'] = event
		if event in self._handler:
			for callback in self._handler[event]:
				result = callback(eventData)
				if result == False:
					return self
		for callback in self._handler['*']:
			result = callback(eventData)
			if result == False:
				break
		return self

	def log(self, msg):
		self._print('INFO:  %s' % msg)
		return self

	def debug(self, msg):
		self._print('DEBUG: %s' % msg)
		return self

	def error(self, msg):
		self._print('ERROR: %s' % msg)
		return self

	def _print(self, msg):
		if self._debug:
			self._log.write("%s %s\n" % (datetime.datetime.now().isoformat()[:-7], msg))
		return self

	def dir(self, id, *args):
		if id in self._dir:
			if args:
				return os.path.join(self._dir[id], *args)
			else:
				return self._dir[id]
		return None

	def str(self, id):
		return self._addon.getLocalizedString(id)

	def path(self, funcName=None, cache=0, **kwargs):
		if funcName and funcName.find('/') == -1:
			if funcName in self._routes:
				uri = self._routes[funcName]
				for name, value in kwargs.items():
					uri = uri.replace('{{'+name+'}}', urllib.quote_plus(str(value)))
				return 'plugin://' + self._id + uri
			else:
				return 'plugin://' + self._id + '/' + funcName + '?' + urllib.urlencode(kwargs)
		elif funcName:
			uri = self._url
			varname = []
			for var in self._urlVarsRE.findall(funcName):
				varname.append(var)
			patternRE = re.compile('^' + self._urlVarsRE.sub('([^/]+)', funcName) + '$')
			def decorator(func):
				self._routes[func.__name__] = funcName
				m = patternRE.findall(uri)
				if m:
					args = {}
					if varname:
						if isinstance(m[0], tuple):
							for i, value in enumerate(m[0]):
								args[varname[i]] = urllib.unquote_plus(value)
						else:
							for i, value in enumerate(m):
								args[varname[i]] = urllib.unquote_plus(value)
					self._match = {'cb': func, 'args': args, 'cache': 0}
			return decorator
		else:
			def decorator(func):
				if self._urlFunc == func.__name__:
					funcArgs = inspect.getargspec(func).args
					urlArgs = dict((k, self._urlArgs[k][0]) for k in funcArgs)
					self._match = {'cb': func, 'args': urlArgs, 'cache': cache}
			return decorator

	def end(self):
		_error = None
		if self._plugin:
			self.debug('Routing: %s%s' % (sys.argv[0], sys.argv[2]))
		else:
			self.debug('Routing: %s' % (sys.argv))
		try:
			if self._match:
				funcSig =  '%s(%s)' % (self._match['cb'].__name__, ', '.join(['%s=\'%s\'' % (key, value) for (key, value) in self._match['args'].items()]))
				if self._match['cache']:
					cacheFile = 'cache.%s' % funcSig
					if not self.storage.expired(cacheFile, self._match['cache']):
						self.debug('Loading cached version: %s' % (funcSig))
						items = self.storage.get(cacheFile)
					else:
						self.debug('Cached version expired')
						self.debug('Redirecting and caching: %s' % (funcSig))
						items = self._match['cb'](**self._match['args'])
						self.storage.set(cacheFile, items)
				else:
					self.debug('Redirecting: %s' % (funcSig))
					items = self._match['cb'](**self._match['args'])
				if isinstance(items, list):
					self.debug('Building directory')
					self.directory.build(items, True, 'tvshows', [25, 31, 17])
					self.debug('Directory built sucessfuly')
			self.storage.flush()
		except:
			_error = 'Exception thrown with the following details:\n%s\n  %s: %s' % ('\n'.join(traceback.format_tb(sys.exc_info()[2])), sys.exc_info()[0].__name__, sys.exc_info()[1])
			self.error(_error)
		finally:
			self.debug('--------------------------')
			if self._debug:
				self._log.close()
			if _error:
				raise


	def wait(self, callback=None, interval=300, timeout=0):
		countdown = timeout
		while not xbmc.abortRequested:
			if timeout > 0:
				if countdown <= 0:
					break
				countdown -= interval
			if callback and not callback():
				break
			xbmc.sleep(interval)
		return self

class AddonSettings:
	def __init__(self, id, addon):
		self._id = id
		self._addon = addon
		self._settingsPath = os.path.join(xbmc.translatePath(self._addon.getAddonInfo('profile')).decode("utf-8"), 'settings.xml')
		self._settingsDialog = None

	def open(self, id1=None, id2=None, id3=None):
		if id1 == None and id2 == None:
			self._addon.openSettings()
		else:
			xbmc.executebuiltin('Addon.OpenSettings(%s)' % self._id)
			if id1 != None:
				xbmc.executebuiltin('SetFocus(%i)' % (id1 + 200))
			if id2 != None:
				xbmc.executebuiltin('SetFocus(%i)' % (id2 + 100))
		return self

	@property
	def mutate(self):
		if not self._settingsDialog:
			self._settingsDialog = AddonSettingsDialog(self._id, self._addon)
		return self._settingsDialog

	def get(self, id, cast=None, default=None):
		value = None
		if id.find('[]') > -1:
			prefix = id[0:-1]
			values = []
			f = xbmcvfs.File(self._settingsPath)
			settings = xmltodict.parse(f)
			f.close()
			for s in settings['settings']['setting']:
				if '@id' in s and s['@id'].find(prefix) == 0 and '@value' in s and s['@value'] != '':
					if cast:
						values.append(cast(s['@value']))
					else:
						values.append(s['@value'])
			value = values
		else:
			value = self._addon.getSetting(id)
			if value != '' and cast:
				value = cast(value)
		return value

	def set(self, *args):
		if len(args) == 2:
			self._addon.setSetting(args[0], str(args[1]))
		else:
			for id, value in args[0].items():
				self._addon.setSetting(id, str(value))
		return self

class AddonSettingsDialog:
	def __init__(self, id, addon):
		self._id = id
		self._addon = addon
		f = xbmcvfs.File(os.path.join(self._addon.getAddonInfo('path'), 'resources', 'settings.xml'))
		self._settings = xmltodict.parse(f.read())
		f.close()
		self._values = None

	def add(self, arg1, arg2, arg3=None):
		if arg3:
			cat = arg1
			index = arg2
			settings = arg3
			if 'settings' not in self._settings or 'category' not in self._settings['settings']:
				return self
			n = len(self._settings['settings']['category'])
			if cat < 0:
				cat = n + cat
			cat = max(min(cat, n - 1), 0)
			if 'setting' not in self._settings['settings']['category'][cat]:
				self._settings['settings']['category'][cat]['setting'] = []
			n = len(self._settings['settings']['category'][cat]['setting'])
			if index < 0:
				index = n + index + 1
			index = max(min(index, n), 0)
			if not isinstance(settings, list):
				settings = [settings]
			for setting in settings:
				self._settings['settings']['category'][cat]['setting'].insert(index, setting)
				index += 1
		else:
			index = arg1
			settings = arg2
			if 'settings' not in self._settings:
				self._settings['settings'] = {}
			if 'category' not in self._settings['settings']:
				self._settings['settings']['category'] = []
			n = len(self._settings['settings']['category'])
			if index < 0:
				index = n + index + 1
			index = max(min(index, n), 0)
			if not isinstance(settings, list):
				settings = [settings]
			for setting in settings:
				self._settings['settings']['category'].insert(index, setting)
				index += 1
		return self

	def remove(self, arg1, arg2=None, arg3=None, removeValues=False):	
		if arg3:
			cat = arg1
			start = arg2
			end = arg3
			if 'settings' not in self._settings or 'category' not in self._settings['settings']:
				return self
			n = len(self._settings['settings']['category'])
			if cat < 0:
				cat = n + cat
			cat = max(min(cat, n - 1), 0)
			if 'setting' not in self._settings['settings']['category'][cat]: 
				return self
			n = len(self._settings['settings']['category'][cat]['setting'])
			if start < 0:
				start = n + start
			start = max(min(start, n - 1), 0)
			if end == None:
				end = start + 1
			if end < 0:
				end = n + end + 1
			end = max(min(end, n), 0)
			if end < start:
				start = end
			if start != end:
				if removeValues:
					sub = self._settings['settings']['category'][cat]['setting'][start:end]
					ids = []
					for s in sub:
						if '@id' in s:
							ids.append(s['@id'])
					self._removeValues(ids)
				del self._settings['settings']['category'][cat]['setting'][start:end]
		else:
			start = arg1
			end = arg2
			if 'settings' not in self._settings or 'category' not in self._settings['settings']:
				return self
			n = len(self._settings['settings']['category'])
			if start < 0:
				start = n + start
			start = max(min(start, n - 1), 0)
			if end == None:
				end = start + 1
			if end < 0:
				end = n + end + 1
			end = max(min(end, n), 0)
			if end < start:
				start = end
			if start != end:
				if removeValues:
					sub = self._settings['settings']['category'][start:end]
					ids = []
					for c in sub:
						if 'setting' in c:
							for s in c['setting']:
								if '@id' in s:
									ids.append(s['@id'])
					self._removeValues(ids)
				del self._settings['settings']['category'][start:end]
		return self

	def _removeValues(self, ids):
		if not self._values:
			f = xbmcvfs.File(os.path.join(self._addon.getAddonInfo('profile'), 'settings.xml'))
			self._values = xmltodict.parse(f.read())
			f.close()
		values = {'settings': {'setting': []}}
		for v in self._values['settings']['setting']:
			if '@id' not in v or v['@id'] not in ids:
				values['settings']['setting'].append(v)
		self._values = values
		return self


	def save(self):
		f = xbmcvfs.File(os.path.join(self._addon.getAddonInfo('path'), 'resources', 'settings.xml'), 'w')
		f.write(str(xmltodict.unparse(self._settings, pretty=True)))
		f.close()
		if self._values:
			f = xbmcvfs.File(os.path.join(self._addon.getAddonInfo('profile'), 'settings.xml'), 'w')
			f.write(str(xmltodict.unparse(self._values, pretty=True)))
			f.close()
		return self
		

class AddonDirectory:
	def __init__(self, addon):
		self._addon = addon
		self.atPath = {
			'@addonsettings': 'Addon.OpenSettings(%s)' % (self._addon.getAddonInfo('id'))
		}

	def viewMode(self, viewMode=None):
		if viewMode:
			xbmc.executebuiltin('Container.SetViewMode(%d)' % viewMode)
			return self
		else:
			return None

	def listItem(self, label, path, label2=None, iconImage=None, thumbnailImage=None, type=None, infoLabels=None, property=None, art=None, streamInfo=None, contextMenu=None, replaceContextMenu=False, selected=None, isFolder=True):
		listItem = xbmcgui.ListItem()
		listItem.setLabel(label)
		listItem.setPath(path)
		if label2:
			listItem.setLabel2(label2)
		if iconImage:
			listItem.setIconImage(iconImage)
		if thumbnailImage:
			listItem.setThumbnailImage(thumbnailImage)
		if type and infoLabels:
			listItem.setInfo(type, infoLabels)
		if property:
			for key in property:
				listItem.setProperty(key, property[key])
		if art and listItem.setArt:
			listItem.setArt(art)
		if streamInfo:
			for t in ['video', 'audio', 'subtitle']:
				if t in streamInfo:
					if not isinstance(streamInfo[t], list):
						streamInfo[t] = [streamInfo[t]]
					for v in streamInfo[t]:
						listItem.addStreamInfo(t, v)
		if contextMenu:
			for item in contextMenu:
				if isinstance(item[0], int):
					item[0] = self._addon.getLocalizedString(item[0])
				if item[1][0] == '@':
					if item[1].lower() in self.atPath:
						item[1] = self.atPath[item[1].lower()]
					else:
						item[1] = 'ActivateWindow(%s)' % item[1][1:]
				elif item[1][:9] == 'plugin://':
					item[1] = 'RunPlugin(%s)' % item[1]
				elif item[1][-3:] == '.py':
					item[1] = 'RunScript(%s)' % item[1]
			listItem.addContextMenuItems(contextMenu, replaceContextMenu)
		elif replaceContextMenu:
			listItem.addContextMenuItems([], replaceContextMenu)
		if selected:
			listItem.select(selected)
		return listItem
		
	def add(self, *args, **kwargs):
		if kwargs:
			xbmcplugin.addDirectoryItem(int(sys.argv[1]), kwargs.get('path', ''), self.listItem(**kwargs), kwargs.get('isFolder', False), kwargs.get('totalItems', 0))
		elif len(args) == 1:
			if isinstance(args[0], list):
				items = []
				for item in args[0]:
					items.append((item.get('path', ''), self.listItem(**item), item.get('isFolder', False),))
				xbmcplugin.addDirectoryItems(int(sys.argv[1]), items, len(items))
			else:
				xbmcplugin.addDirectoryItem(int(sys.argv[1]), args[0].get('path', ''), self.listItem(**args[0]), args[0].get('isFolder', False), args[0].get('totalItems', 0))
		return self

	def content(self, content):
		if content:
			xbmcplugin.setContent(int(sys.argv[1]), content)
		return self

	def sortMethods(self, methods):
		if methods:
			if isinstance(methods, list):
				for method in methods:
					xbmcplugin.addSortMethod(int(sys.argv[1]), method)
			else:
				xbmcplugin.addSortMethod(int(sys.argv[1]), methods)
		return self

	def end(self, succeeded=True, updateListing=False, cacheToDisc=True):
		xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded, updateListing, cacheToDisc)

	def build(self, items, succeeded=True, content=None, sortMethods=None, updateListing=False, cacheToDisc=True):
		self.content(content).sortMethods(sortMethods).add(items).end(succeeded, updateListing, cacheToDisc)

class AddonDialog:
	def __init__(self, addon):
		self._addon = addon
		self._dialog = xbmcgui.Dialog()
		self._progress = xbmcgui.DialogProgress()
		self._progressBG = xbmcgui.DialogProgressBG()
	def browse(self, type, heading, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		return self._dialog.browse(type, heading, *args)
	def input(self, heading, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		return self._dialog.input(heading, *args)
	def notification(self, heading, message, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		if isinstance(message, int):
			message = self._addon.getLocalizedString(message)
		return self._dialog.notification(heading, message, *args)
	def numeric(self, heading, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		return self._dialog.numeric(heading, *args)
	def ok(self, heading, message, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		if isinstance(message, int):
			message = self._addon.getLocalizedString(message)
		return self._dialog.ok(heading, message, *args)
	def select(self, heading, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		return self._dialog.select(heading, *args)
	def yesno(self, heading, message, *args):
		if isinstance(heading, int):
			heading = self._addon.getLocalizedString(heading)
		if isinstance(message, int):
			message = self._addon.getLocalizedString(message)
		return self._dialog.yesno(heading, message, *args)
	def progress(self, title, message=None, background=False):
		if background:
			self._progressBG.create(title, message)
			self._progressBG.update(0, title, message)
			return self._progressBG
		else:
			self._progress.create(title, message)
			self._progress.update(0, message)
			return self._progress

class AddonStorage:
	def __init__(self, addon):
		self._path = xbmc.translatePath(addon.getAddonInfo('profile')).decode("utf-8")
		self._data = {}

	def expired(self, id, ttl):
		path = os.path.join(self._path, id.replace('.', os.path.sep) + '.json')
		stat = xbmcvfs.Stat(path)
		if not os.path.isfile(path) or time.time() - stat.st_mtime(path) > ttl:
			return True
		return False

	def get(self, id):
		if not id in self._data:
			self._data[id] = {}
			path = os.path.join(self._path, id.replace('.', os.path.sep) + '.json')
			if os.path.isfile(path):
				fp = xbmcvfs.File(path)
				self._data[id] = json.load(fp)
				fp.close()
		return self._data[id]

	def set(self, id, data):
		self._data[id] = data
		return self

	def flush(self, id=None):
		if id:
			self._flush(id)
		else:
			for id, data in self._data.items():
				self._flush(id)
		return self

	def _flush(self, id):
		if id in self._data and self._data[id]:
			path = os.path.join(self._path, id.replace('.', os.path.sep) + '.json')
			dirs = os.path.dirname(path)
			if not os.path.isdir(dirs):
				xbmcvfs.mkdirs(dirs)
			fp = xbmcvfs.File(path, 'w')
			json.dump(self._data[id], fp)
			fp.close()

	def purge(self, id=None):
		path = os.path.join(self._path, id.replace('.', os.path.sep) + '.json')
		if os.path.isfile(path):
			os.remove(path)
			self._purge(os.path.dirname(path))
		return self

	def _purge(self, path):
		files = os.listdir(path)
		if files:
			for f in files:
				fullpath = os.path.join(path, f)
				if os.path.isdir(fullpath):
					self._purge(fullpath)

		else:
			os.rmdir(path)

class AddonPlayer(xbmc.Player):
	def __init__(self, *args):
		xbmc.Player.__init__(self, *args)

	def _setTriggerer(self, trigger):
		self._trigger = trigger

	def _getData(self):
		data = {'sender': 'xbmc', 'data': {}}
		try:
			data['data']['file'] = self.getPlayingFile()
			data['data']['streams'] = {}
			data['data']['audio'] = self.getAvailableAudioStreams()
			data['data']['subtitles'] = self.getAvailableSubtitleStreams()
			data['data']['subtitle'] = self.getSubtitles()
			data['data']['time'] = self.getTime()
			data['data']['totalTime'] = self.getTotalTime()
			data['data']['playing'] = self.isPlaying()
		except:
			pass
		try:
			#data['data']['info'] = {}
			infoTag = self.getVideoInfoTag()
			members =  inspect.getmembers(infoTag)
			for m in members:
				if m[0][:3] == 'get':
					data['data'][m[0][3:4].lower() + m[0][4:]] = m[1]()
		except:
			try:
				#data['data']['info'] = {}
				infoTag = self.getMusicInfoTag()
				members =  inspect.getmembers(infoTag)
				for m in members:
					if m[0][:3] == 'get':
						data['data'][m[0][3:4].lower() + m[0][4:]] = m[1]()
			except:
				pass
		return data

	def onPlayBackStarted(self):
		data = self._getData()
		self._trigger('playbackstarted', data)
	def onPlayBackPaused(self):
		data = self._getData()
		self._trigger('playbackpaused', data)
	def onPlayBackResumed(self):
		data = self._getData()
		self._trigger('onplaybackresumed', data)
	def onPlayBackSeek(self, time, seekOffset):
		data = self._getData()
		data.update({'time': time, 'seekOffset': seekOffset})
		self._trigger('onplaybackseek', data)
	def onPlayBackSeekChapter(self, chapter):
		data = self._getData()
		data.update({'chapter': chapter})
		self._trigger('onplaybackseekchapter', data)
	def onPlayBackSpeedChanged(self, speed):
		data = self._getData()
		data.update({'speed': speed})
		self._trigger('onplaybackspeedchanged', data)
	def onPlayBackStopped(self):
		self._trigger('playbackstopped')
	def onPlayBackEnded(self):
		self._trigger('playbackended')
	def onQueueNextItem(self):
		self._trigger('onqueuenextitem')

	def playSync(self, *args, **kwargs):
		if 'interval' in kwargs:
			interval = kwargs['interval']
		else:
			interval = 300
		self.play(*args, **kwargs)
		self.wait(self.isPlaying, interval)

	def wait(self, callback=None, interval=300, timeout=0):
		countdown = timeout
		while not xbmc.abortRequested:
			if timeout > 0:
				if countdown <= 0:
					break
				countdown -= interval
			if callback and not callback():
				break
			xbmc.sleep(interval)

class AddonMonitor(xbmc.Monitor):
	def __init__(self, *args):
		xbmc.Monitor.__init__(self, *args)

	def _setTriggerer(self, trigger):
		self._trigger = trigger

	def onAbortRequested(self):
		self._trigger('abortrequested')
	def onDatabaseScanStarted(self, database):
		self._trigger('databasescanstarted', {'database': database})
	def onDatabaseUpdated(self, database):
		self._trigger('databaseupdated', {'database': database})
	def onNotification(self, sender, method, data):
		self._trigger('notification', {'sender': sender, 'method': method, 'data': data})
	def onScreensaverActivated(self):
		self._trigger('screensaveractivated')
	def onScreensaverDeactivated(self):
		self._trigger('screensaverdeactivated')
	def onSettingsChanged(self):
		self._trigger('settingschanged')

	def wait(self, callback=None, interval=300, timeout=0):
		countdown = timeout
		while not xbmc.abortRequested:
			if timeout > 0:
				if countdown <= 0:
					break
				countdown -= interval
			if callback and not callback():
				break
			xbmc.sleep(interval)
	

class AddonVirtualFileSystem:
	def __init__(self):
		pass

	def open(self, *args):
		return xbmcvfs.File(*args)

	def stats(self, *args):
		info = {}
		st = xbmcvfs.Stat(*args)
		info['atime'] = st.st_atime()
		info['ctime'] = st.st_ctime()
		info['mtime'] = st.st_mtime()
		info['mode'] = st.st_mode()
		info['ino'] = st.st_ino()
		info['gid'] = st.st_gid()
		info['uid'] = st.st_uid()
		info['nlink'] = st.st_nlink()
		info['size'] = st.st_size()
		info['dev'] = st.st_dev()

	def exists(self, *args):
		return xbmcvfs.exists(*args)
	def copy(self, *args):
		return xbmcvfs.copy(*args)
	def rename(self, *args):
		return xbmcvfs.rename(*args)
	def delete(self, *args):
		return xbmcvfs.delete(*args)
	def listdir(self, *args):
		return xbmcvfs.listdir(*args)
	def mkdir(self, *args):
		return xbmcvfs.mkdir(*args)
	def mkdirs(self, *args):
		return xbmcvfs.mkdirs(*args)
	def rmdir(self, *args):
		return xbmcvfs.rmdir(*args)

# TODO: complete and improve the evented interaction to include action filtering.
# TODO: subclass other controls to implement evented interactions
# TODO: create layout manager and adjust the add method
class AddonWindow(xbmcgui.Window):
	#def __new__(cls, *args):
	#	return super(AddonWindow, cls).__new__(cls, *args)

	def __init__(self, *args):
		super(AddonWindow, self).__init__(*args)
		self._handler = {'*': []}

	def onFocus(self, id):
		control = self.getControl(id)
		self.trigger('focus', {'target': control})

	def onControl(self, control):
		self.trigger('control', {'target': control})

	def onAction(self, action):
		self.trigger('action', {'action': action})

	def onClick(self, id):
		control = self.getControl(id)
		self.trigger('click', {'target': control})

	def onDoubleClick(self, id):
		control = self.getControl(id)
		self.trigger('doubleclick', {'target': control})

	def on(self, event, arg1, arg2=None):
		if arg2:
			actions = arg1
			callback = arg2
		else:
			actions = []
			callback = arg1
		event = event.lower()
		if not event in self._handler:
			self._handler[event] = []
		self._handler[event].append(callback)
		return self

	def off(self, event, callback=None):
		event = event.lower()
		if event in self._handler:
			if callback:
				self._handler[event][:] = [cb for cb in self._handler[event] if callback == cb]
			else:
				del self._handler[event]
		return self

	def trigger(self, event, eventData={}):
		event = event.lower()
		eventData['name'] = event
		if event in self._handler:
			for callback in self._handler[event]:
				callback(eventData)
		for callback in self._handler['*']:
			callback(eventData)
		return self

	def layoutManager(self, layout):
		pass
		
	def add(self, controls):
		if isinstance(controls, list):
			self.addControls(controls)
		else:
			self.addControl(controls)

	def show(self, modal=False):
		if modal:
			self.doModal()
		else:
			super(AddonWindow, self).show()
