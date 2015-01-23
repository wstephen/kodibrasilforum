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
from spotlight.model.Settings import Settings
from spotify import image, link, playlist, handle_sp_error
from spotify.playlist import Playlist, PlaylistType
from spotify.link import LinkType
import ctypes
from spotify.track import TrackAvailability

class ModelFactory:

    def __init__(self, url_gen):
        self.url_gen = url_gen
        self.settings = Settings()
    
    def to_album_model(self, album):
        
        return Model(
                name=album.name(),
                year=album.year(),
                image=self.url_gen.get_image_url(album.cover(image.ImageSize.Large)),
                uri=self.url_gen.get_album_uri(album))
    
    def to_track_model(self, track, session):
        
        track_artist_names = [artist.name() for artist in track.artists()]
        return Model(track=self.get_track_name(track, session),
                     album=self.get_album_name(track),                     
                     artist=", ".join(track_artist_names),
                     uri=link.create_from_track(track).as_string(),
                     type=link.create_from_track(track).type(),
                     album_uri=self.url_gen.get_album_uri(track.album()),
                     iconImage=self.url_gen.get_icon_url(track),
                     thumbnailImage=self.url_gen.get_thumbnail_url(track),
                     path=self.get_track_path(track, session),
                     time=track.duration() / 1000)

    def get_track_path(self, track, session):
        path = "http://127.0.0.1/spotlight/empty-track/"
        if not track.get_availability(session) is TrackAvailability.Available:
            # Use unique nonexistent URL for nonavailable tracks. Otherwise
            # XBMC treats all nonavailable tracks as one.
            path += link.create_from_track(track).as_string()
        else:
            path=self.url_gen.get_track_url(track)
        
        return path

    def get_track_name(self, track, session):
        name = '[not available]'
        if track.name() is not None:
            if not track.get_availability(session) is TrackAvailability.Available: 
                name = track.name() + ' [not available]'
            else:
                name = track.name()    
            
        return name    
        
    def get_album_name(self, track):
        if track.album() is not None:
            return track.album().name()
        return '';

    # Fix for a bug in pyspotify-ctypes
    def playlist_folder_name(self, container, index):
        buf = ctypes.create_string_buffer(255)
        handle_sp_error(
            container._PlaylistContainer__container_interface.playlist_folder_name(
                container._PlaylistContainer__container_struct, index, buf, 255
            )
        )
        return buf.value
        
    def to_playlist_list_model(self, playlists):
        
        return [self.to_playlist_model(playlist, index) for index, playlist in enumerate(playlists)]
        
    def to_playlist_list_model_from_container(self, container):
        without_nested = []        
        ignore = False
        for index in range(0, container.num_playlists() - 1):
            playlist = container.playlist(index)
            playlist_type = container.playlist_type(index)
            if playlist_type is PlaylistType.StartFolder:
                ignore = True
                without_nested.append(self.to_playlist_model(
                                                             playlist, 
                                                             index, 
                                                             self.playlist_folder_name(container, index),
                                                             container.playlist_folder_id(index))) 
            if playlist_type is PlaylistType.EndFolder:
                ignore = False
            elif not ignore:
                without_nested.append(self.to_playlist_model(playlist, index))
            
        return without_nested
   
    def to_playlist_model(self, playlist, index, folder_name = None, folder_id = 0):

        return Model(name = self.playlist_name(playlist, folder_name), 
                     owner = playlist.owner().display_name(), 
                     index = index, 
                     uri = self.playlist_uri(playlist), 
                     is_folder = folder_name is not None, 
                     folder_id = str(folder_id))
    
    def playlist_name(self, playlist, folder_name):
        name = ''
        if folder_name is not None:
            name = folder_name
        else:
            name = playlist.name()
        return name
    
    def playlist_uri(self, playlist):
        playlist_link = link.create_from_playlist(playlist)
        uri = ''
        if playlist_link is not None:
            uri = playlist_link.as_string()
            
        return uri
    
    def to_artist_model(self, artist):
        
        return Model(name = artist.name(), uri = link.create_from_artist(artist).as_string())
    
    def to_track_list_model(self, tracks, session):
        if self.settings.show_missing:
            return [self.to_track_model(track, session) for track in tracks]
        else:
            # Do not display nonavailable tracks
            return [self.to_track_model(track, session) for track in tracks
                    if track.get_availability(session) is TrackAvailability.Available]
    
    def to_album_list_model(self, albums):
    
        return map(lambda album:self.to_album_model(album), albums)
    
    def to_artist_list_model(self, artists):
    
        return map(lambda artist:self.to_artist_model(artist), artists)
    
    def to_inbox_model(self, items, session):
        track_links = [link.create_from_track(track) for track in items]
                           
        albums = [track_link.as_album() 
                  for track_link in track_links if track_link.type() is LinkType.Album]
        artists = [track_link.as_artist() 
                   for track_link in track_links if track_link.type() is LinkType.Artist]
        tracks = [track_link.as_track() 
                  for track_link in track_links if track_link.type() is LinkType.Track]
        playlists = [Playlist(playlist.create(session, track_link)) 
                     for track_link in track_links if track_link.type() is LinkType.Playlist]
        
        return Model(albums = self.to_album_list_model(albums),
                     artists = self.to_artist_list_model(artists),
                     tracks = self.to_track_list_model(tracks, session),
                     playlists = self.to_playlist_list_model(playlists))
    
    def clean_up(self):
        self.url_gen.clean_up()
        
