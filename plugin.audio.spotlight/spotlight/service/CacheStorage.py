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
from threading import Lock
import time

class Cache:
    
    def __init__(self, name, settings):
        self.name = name        
        self.lock = Lock()
        self.settings = settings
        self.invalidate()
                
    def invalidate(self):
        self.map = {}
        self.time = time.time()
        
    def update(self, key, value):
        self.lock.acquire()
        self.map[key] = value
        self.lock.release()
        
    def get(self, key):
        self.lock.acquire()
        if self.should_invalidate():
            self.invalidate()
        value = None
        if self.enabled():    
            value = self.map.get(key)
            self.time = time.time()         
        self.lock.release()
        
        return value
    
    def get_max_age(self):
        
        return self.settings.max_playlists_cache_age
    
    def enabled(self):
        
        return self.settings.enable_playlists_cache
    
    def should_invalidate(self):
        if self.get_max_age() <= 0:
            return False
        
        return time.time() - self.time > self.get_max_age() 
        
        
class CacheStorage:
    
    caches = {}
    
    def __init__(self, settings):
        self.lock = Lock()
        self.settings = settings        
        
    def get_cache(self, key):
        self.lock.acquire()
        cache = self.caches.get(key)
        if cache is None:
            cache = Cache(key, self.settings)
            self.caches[key] = cache
        self.lock.release()
        return cache
                 
    def invalidate(self, key):
        self.lock.acquire()
        cache = self.caches.get(key)
        if cache is not None:
            cache.invalidate()
        self.lock.release()
          
    def invalidate_all(self):
        self.lock.acquire()
        for key, value in self.caches.iteritems() :
            value.invalidate()
        self.lock.release()
            
            
        
        
    