# 
#  Copyright (c) Dariusz Biskup
#  
#  This file is part of Spotlight
# 
#  Spotlight is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation; either version 3 of 
#  the License, or (at your option) any later version.
#  
#  Spotlight is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#  

from spotlight.model.Model import Model
from spotlight.ui.Router import Router
from spotlight.ui.Paths import Paths
import sys
import xbmcplugin
import xbmc
import xbmcgui
from spotlight.model.Page import Page
from spotlight.model.GlobalSettings import GlobalSettings
import xbmcaddon

class UiHelper:
    
    DEFAULT_FOLDER_IMG = 'DefaultFolder.png'
    RUN_PLUGIN_SCRIPT = 'XBMC.RunPlugin(%s)'
    UPDATE_CONTAINER_SCRIPT = 'XBMC.Container.Update(%s)' 
    CONTENT_SONGS = 'songs'
    CONTENT_ALBUMS = 'albums'
    CONTENT_ARTISTS = 'artists'

    def __init__(self, list_item_factory, settings):
        self.addon_handle = int(sys.argv[1])
        self.add_on = xbmcaddon.Addon(GlobalSettings.ADD_ON_ID)    
        self.list_item_factory = list_item_factory
        self.settings = settings
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_ALBUMS)
    
    def keyboardText(self):        
        keyboard = xbmc.Keyboard('', self.add_on.getLocalizedString(30033))
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText()     
        
        return None
    
    def create_folder_item(self, title, url, image = DEFAULT_FOLDER_IMG):
        item = xbmcgui.ListItem(title, iconImage = image)
                
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, 
                                    url = url, listitem = item, 
                                    isFolder = True)       
         
    def create_list_of_playlists(self, playlists, show_owner = False):
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_ALBUMS)
        
        for playlist in playlists:
            url = self.get_playlist_url(playlist)
            self.create_folder_item(self.format_playlist_name(playlist, show_owner), url)
        
    def get_playlist_url(self, playlist):
        if playlist.is_folder:
            return Router.url_for(Paths.FOLDER_PLAYLISTS, Model(folder_id = playlist.folder_id))
        else: 
            return Router.url_for(Paths.GET_PLAYLIST, self.settings.initial_page_for_pagination(playlist.uri))         
         
    def format_playlist_name(self, playlist, show):
        if playlist.owner is None or show is False:
            return self.add_bold(playlist.name, when = playlist.is_folder)
        
        return self.add_bold('%s [I]%s %s[/I]' % (playlist.name, self.add_on.getLocalizedString(30034), playlist.owner), when = playlist.is_folder)

    def add_bold(self, text, when):
        if when:
            return '[B]%s[/B]' % text
        
        return text
         
    def create_list_of_tracks(self, tracks, page = Page(), path = None):
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_SONGS)
        xbmcplugin.addSortMethod(self.addon_handle, xbmcplugin.SORT_METHOD_TRACKNUM)
        xbmcplugin.addSortMethod(self.addon_handle, xbmcplugin.SORT_METHOD_ARTIST)
        xbmcplugin.addSortMethod(self.addon_handle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(self.addon_handle, xbmcplugin.SORT_METHOD_ALBUM)
                
        self.create_track_list_items(tracks, page)
        
        if page.has_next():
            self.create_folder_item(self.add_on.getLocalizedString(30029), Router.url_for(path, page.next()))
        
    def create_list_of_albums(self, albums):
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_ALBUMS)
        
        for album in albums:
            url = Router.url_for(Paths.ALBUM_TRACKS, Model(album = album.uri))
            self.create_folder_item('%s [%s]' % (album.name, album.year), url, album.image)
            
    def create_list_of_artists(self, artists):
        xbmcplugin.setContent(self.addon_handle, UiHelper.CONTENT_ARTISTS)
        
        for artist in artists:
            url = Router.url_for(Paths.ARTIST_ALBUMS, Model(artist = artist.uri))
            self.create_folder_item('%s' % (artist.name), url)

    def create_track_list_items(self, tracks, page = Page()):
        indexes = range(0, len(tracks))        
        if not page.is_infinite():
            indexes = page.current_range()
        for index in indexes:                        
            track = tracks[index - page.start]
            path, item = self.list_item_factory.create_list_item(track, index + 1)
            self.add_context_menu(track, path, item)
            
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url = path, listitem=item)            

    def add_context_menu(self, track, play_url, li):
        browse_album_url = Router.url_for(Paths.ALBUM_TRACKS, Model(album = track.album_uri))
        browse_artist_url = Router.url_for(Paths.ARTIST_ALBUMS_FOR_TRACK, Model(track = track.uri))
        
        li.addContextMenuItems([(self.add_on.getLocalizedString(30032), UiHelper.RUN_PLUGIN_SCRIPT % play_url), 
                                (self.add_on.getLocalizedString(30031), UiHelper.UPDATE_CONTAINER_SCRIPT % browse_album_url), 
                                (self.add_on.getLocalizedString(30030), UiHelper.UPDATE_CONTAINER_SCRIPT % browse_artist_url)])       

    def end_directory(self):
        xbmcplugin.endOfDirectory(self.addon_handle)