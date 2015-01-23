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

from spotlight.service.util.SynchronizerMixin import SynchronizerMixin
from spotify.playlist import PlaylistCallbacks

class LoadStarred(SynchronizerMixin, PlaylistCallbacks):
    
    def __init__(self, session):
        self.session = session
    
    def before_wait(self):
        self.playlist.add_callbacks(self)        
    
    def execute(self):
        self.playlist = self.session.starred_create()
        
        if self.playlist.is_loaded():
            self.disable_wait()
        
        return self.playlist
    
    def playlist_state_changed(self, playlist):
        if playlist.is_loaded(): 
            self.done()
            
    def clean_up(self):
        self.playlist.remove_callbacks(self)