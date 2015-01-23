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
from spotify.session import SessionCallbacks
from spotify import link


class LoadTrack(SynchronizerMixin, SessionCallbacks):
    
    def __init__(self, track, session):
        self.track = track
        self.session = session
        
    def before_wait(self):
        self.session.add_callbacks(self)
    
    def execute(self):
        if self.track.is_loaded():
            self.disable_wait()
         
        return self.track
    
    def metadata_updated(self, session):
        if self.track.is_loaded():
            self.done(None)
            
    def clean_up(self):
        self.session.remove_callbacks(self)
        
    @staticmethod        
    def from_uri(uri, session):
        track_link = link.create_from_string(uri)
        track = track_link.as_track()
        return LoadTrack(track, session).run_and_wait()

    @staticmethod
    def from_list(tracks, session):
        return filter(lambda track : track.is_loaded(), 
                      map(lambda track : LoadTrack(track, session).run_and_wait(), tracks))
