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

from spotify.playlistcontainer import PlaylistContainerCallbacks

class PlaylistCallbacks(PlaylistContainerCallbacks):
    
    def __init__(self, cache_storage):
        self.cache_storage = cache_storage
    
    def playlist_added(self, container, playlist, position):
        print 'Invalidating cache.'
        self.cache_storage.invalidate_all()
        
    def playlist_removed(self, container, playlist, position):
        print 'Invalidating cache.'
        self.cache_storage.invalidate_all()
    
    def playlist_moved(self, container, playlist, position, new_position):
        print 'Invalidating cache.'
        self.cache_storage.invalidate_all()
    
    def container_loaded(self, container):
        print 'Invalidating cache.'
        self.cache_storage.invalidate_all()
    