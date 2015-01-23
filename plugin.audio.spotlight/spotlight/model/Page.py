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

class Page:
        
    def __init__(self, start = 0, offset = 0, max_items = 0, identifier = ''):
        self.start = start
        self.offset = offset
        self.max_items = max_items
        self.identifier = identifier
        self.fix_offset()
        
    def next(self):
        new_start = self.start + self.offset
        new_offset = self.offset
        
        if not self.has_next():
            return None
        
        if new_start + self.offset > self.max_items and self.max_items != 0:
            new_offset = self.max_items - new_start
        
        return Page(new_start, new_offset, self.max_items, self.identifier)
    
    def has_next(self):
        
        return (self.start + self.offset < self.max_items or self.max_items == 0) and not self.is_infinite()
            
    def current_range(self):
        
        return range(self.start, self.start + self.offset)
    
    def is_infinite(self):
        
        return self.start == 0 and self.offset == 0 and self.max_items == 0
    
    def fix_offset(self):
        if self.start + self.offset > self.max_items and self.max_items > 0:
            self.offset = self.max_items - self.start

    def cache_key(self):
        return '%s %s %s %s' % (self.start, self.offset, self.max_items, self.identifier)

    @staticmethod
    def from_obj(obj):
        page = Page() 
        page.start = obj.get('start')
        page.offset = obj.get('offset')
        page.max_items = obj.get('max_items')
        page.identifier= obj.get('identifier')
        
        return page 
        
    @staticmethod        
    def inifinite(identifier = ''):
        
        return Page(0, 0, 0, identifier)
    
        