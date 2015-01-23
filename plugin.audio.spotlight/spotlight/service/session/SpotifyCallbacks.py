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

from spotify.session import SessionCallbacks
from spotify import ErrorType
from spotify import ConnectionState
import weakref
import xbmc

class SpotifyCallbacks(SessionCallbacks):
    
    def __init__(self, server, main_loop, audio_buffer, authenticator):
        self.server = weakref.proxy(server)
        self.main_loop = main_loop
        self.audio_buffer = audio_buffer
        self.authenticator = authenticator
    
    def logged_in(self, session, error):
        
        xbmc.log("libspotify: logged in: %d" % error)
        
        if error != ErrorType.Ok:                        
            self.authenticator.error()
        else:
            self.authenticator.logged_in()
            if self.authenticator.connection_state() == ConnectionState.LoggedIn:
                self.server.set_up_playlistcontainer_callbacks(session)
        
    def logged_out(self, session):
        xbmc.log('Spotify logged out.')
        
    def connection_error(self, session, error):
        xbmc.log("libspotify: conn error: %d" % error)
        self.authenticator.error()
        
    def connectionstate_updated(self, session):
        self.authenticator.logged_in()
        
    def message_to_user(self, session, data):
        xbmc.log("libspotify: msg: %s" % data)
    
    def log_message(self, session, data):
        xbmc.log("libspotify log: %s" % data)
    
    def streaming_error(self, session, error):
        xbmc.log("libspotify: streaming error: %d" % error)
        self.authenticator.error()
        
    def metadata_updated(self, session):
        xbmc.log("libspotify: metadata updated")
        
    def notify_main_thread(self, session):
        xbmc.log("libspotify: notified main thread")
        self.main_loop.notify()
        
    def music_delivery(self, session, data, num_samples, sample_type, sample_rate, num_channels):
        xbmc.log("libspotify: music delivery samples = %d" % num_samples)
        return self.audio_buffer.music_delivery(data, num_samples, sample_type, sample_rate, num_channels)

    def scrobble_error(self, session, error):
        xbmc.log("libspotify: scrobble error: %d" % error)
