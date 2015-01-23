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
from spotify.search import SearchCallbacks
from spotify import search
from spotlight.service.util import encode

class Search(SynchronizerMixin, SearchCallbacks):
    
    def __init__(self, page, session):
        self.page = page
        self.session = session
    
    def execute(self):
        self.search_result = search.Search(
            self.session, encode(self.page.identifier),
            track_offset = self.page.start, track_count = self.page.offset,
            callbacks = self)
        
        return self.search_result
    
    def search_complete(self, result):
        self.done(result)
