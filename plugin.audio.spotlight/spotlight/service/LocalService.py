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

from spotlight.service.util.SessionGuard import SessionGuard
from spotlight.service.command.LoadTrack import LoadTrack
from spotlight.service.command.LoadStarred import LoadStarred
from spotlight.service.command.LoadAlbum import LoadAlbum
from spotlight.service.command.BrowseAlbum import BrowseAlbum
from spotlight.service.command.BrowseArtist import BrowseArtist
from spotlight.service.util.AlbumFilter import AlbumFilter
from spotlight.service.command.Search import Search

from spotlight.service.util import encode
from spotlight.service.command.LoadInbox import LoadInbox
from spotify import playlist, link
from spotify.playlist import Playlist, PlaylistType
from spotlight.service.util.Cached import Cached
from spotlight.model.Model import Model
from spotlight.model.Page import Page


class LocalService:
    
    def __init__(self, server):
        self.server = server
        self.model_factory = server.get_model_factory()
        self.authenticator = server.get_authenticator()   
        self.cache_storage = server.get_cache_storage()     
        
    def start_session(self):
        self.server.start()
        return 'OK'

    def stop_session(self):
        self.server.stop()
        return 'OK'

    def login(self):
        self.server.log_in()
        return 'OK'

    def logout(self):
        self.server.log_out()
        return 'OK'

    def reset(self):
        self.server.reset_settings()
        return 'OK'

    def has_active_session(self):
        return self.server.is_active()

    @SessionGuard
    def search(self, page = {}):
        page = Page.from_obj(page)
        session = self.current_session()
        search_result = Search(page, session).run_and_wait()
        tracks = LoadTrack.from_list(search_result.tracks(), session)
        
        return Model(tracks = self.model_factory.to_track_list_model(tracks, session), page = page)
    
    @SessionGuard
    def starred(self, page = {}):
        session = self.current_session()
        playlist = LoadStarred(session).run_and_wait()
        page = Page.from_obj(page)
        
        return self.tracks_model(playlist, page, session)
    
    def tracks_model(self, playlist, page, session):
        if not page.is_infinite():
            tracks_model = self.partial_result(playlist, page, session)
        else:            
            tracks = LoadTrack.from_list(playlist.tracks(), session)
            tracks_model = Model(tracks = self.model_factory.to_track_list_model(tracks, session), page = Page())
         
        return tracks_model
    
    def partial_result(self, playlist, page, session):
        tracks = []
        page = Page(page.start, page.offset, playlist.num_tracks(), page.identifier)
        
        for i in page.current_range():
            track = playlist.track(i)
            tracks.append(track)
            
        return Model(tracks = self.model_factory.to_track_list_model(tracks, session), page = page)
    
    @SessionGuard
    def inbox(self):
        session = self.current_session()
        result = LoadInbox(session).run_and_wait()
        
        return self.model_factory.to_inbox_model(result.tracks(), session)

    @Cached('playlists')
    @SessionGuard
    def playlists(self):
        session = self.current_session()
        container = session.playlistcontainer()

        return self.model_factory.to_playlist_list_model_from_container(container)

    @Cached('folder_playlists')
    @SessionGuard
    def folder_playlists(self, folder_id):
        session = self.current_session()
        container = session.playlistcontainer()
        add_playlists = False
        playlists = []
        for index in range(0, container.num_playlists() - 1):
            playlist = container.playlist(index)
            playlist_type = container.playlist_type(index)
            if playlist_type is PlaylistType.StartFolder and str(container.playlist_folder_id(index)) == str(folder_id):
                add_playlists = True
            elif playlist_type is PlaylistType.EndFolder:
                add_playlists = False
            elif add_playlists:
                playlists.append(playlist)
                
        return self.model_factory.to_playlist_list_model(playlists)

    @Cached('playlist_tracks')
    @SessionGuard
    def playlist_tracks(self, page = {}):
        page = Page.from_obj(page)
        playlist_link = link.create_from_string(page.identifier)        
        session = self.current_session()
        linked_playlist = Playlist(playlist.create(session, playlist_link))

        return self.tracks_model(linked_playlist, page, session)        
    
    @SessionGuard
    def album_tracks(self, album_uri):
        session = self.current_session()
        album = LoadAlbum.from_uri(album_uri, session)
        browse = BrowseAlbum(album, session).run_and_wait()
        tracks = LoadTrack.from_list(browse.tracks(), session)
    
        return self.model_factory.to_track_list_model(tracks, session)
    
    @SessionGuard
    def artist_albums_from_track(self, track_uri):
        session = self.current_session()
        track = LoadTrack.from_uri(track_uri, session)
        browse = BrowseArtist(track.album().artist(), session).run_and_wait()
        albums = AlbumFilter(browse.albums()).filter()
    
        return self.model_factory.to_album_list_model(albums)
    
    @SessionGuard
    def artist_albums(self, artist_uri):
        session = self.current_session()
        artist = link.create_from_string(artist_uri).as_artist()
        browse = BrowseArtist(artist, session).run_and_wait()
        albums = AlbumFilter(browse.albums()).filter()
    
        return self.model_factory.to_album_list_model(albums)
       
    def current_session(self):
        return self.authenticator.current_session()
    
    
