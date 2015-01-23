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

class AlbumFilter:
    
    def __init__(self, albums):
        self.albums = albums
        
    def filter(self):
        dictionary = {}
        for album in self.albums:
            current_value = dictionary.get(album.name())
            if current_value is None: 
                dictionary[album.name()] = album
                
        return sorted(dictionary.values(), key = lambda album : album.year(), reverse = True)
                 
                
            