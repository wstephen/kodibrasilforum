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

from threading import Event
import xbmc
from spotify import ConnectionState, SocialProvider, ScrobblingState

class Authenticator:
    
    WAIT_TIMEOUT = 10
    
    def __init__(self):
        self.flag = Event()
        self.session = None
    
    def set_session(self, session):
        self.session = session
    
    def login(self, username, password):      
        xbmc.log('Spotlight: Logging in')
        self.check_session()  
        self.session.login(username, password)
        self.flag.wait(Authenticator.WAIT_TIMEOUT)
        xbmc.log('Spotlight: Lock released - %s' % self.connection_state())
        return self.connection_state()

    def logout(self):      
        xbmc.log('Spotlight: Logging out')
        self.check_session()  
        self.session.logout()
        self.flag.wait(Authenticator.WAIT_TIMEOUT)
        xbmc.log('Spotlight: Lock released - %s' % self.connection_state())
        return self.connection_state()
        
    def connection_state(self):
        self.check_session()
        return self.session.connectionstate()
        
    def current_session(self):
        self.check_session()
        return self.session
        
    def logged_in(self):
        xbmc.log('Got logged IN callback')
        self.release_lock_if_logged()

    def logged_out(self):
        xbmc.log('Got logged OUT callback')
        self.release_lock_if_not_logged()
        
    def error(self):
        xbmc.log('Got error callback')
        self.release_lock()
        
    def release_lock_if_logged(self):
        if self.connection_state() == ConnectionState.LoggedIn:
            self.release_lock()

    def release_lock_if_not_logged(self):
        if self.connection_state() == ConnectionState.LoggedOut:
            self.release_lock()
            
    def release_lock(self):
        self.flag.set()
        self.flag.clear()
        
    def check_session(self):
        if self.session is None:
            raise Exception("Spotify session does not exist.")
        
    def clean_up(self):
        self.session = None

    def lastfm_scrobbling(self, enabled, username, password):
        if enabled:
            xbmc.log('Last.fm scrobbling enabled')
            self.session.set_social_credentials(SocialProvider.Lastfm, username, password)
            self.session.set_scrobbling(SocialProvider.Lastfm, ScrobblingState.LocalEnabled)
        else:
            xbmc.log('Last.fm scrobbling disabled')
            self.session.set_scrobbling(SocialProvider.Lastfm, ScrobblingState.LocalDisabled)
