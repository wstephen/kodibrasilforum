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
import types
from spotlight.model.Page import Page


class Cached(object):
    
    GLOBAL_KEY = '_'
    
    def __init__ (self, key):
        self.key = key
    
    def __call__ (self, f):        
        def wrapped_f(*args):
            cache_storage = args[0].cache_storage
            cache = cache_storage.get_cache(self.key)
            item_key = Cached.GLOBAL_KEY

            if len(args) > 1:
                arg = args[1]
                print arg
                if type(arg) == type({}):
                    page = Page.from_obj(arg)
                    item_key = page.cache_key()
                else:
                    item_key = arg
                
            result = cache.get(item_key)
            
            if result is not None:
                print 'Cache hit for item ', item_key, ' and cache ', self.key
                return result
            else:
                print 'Cache miss. Calling function and filling cache item ', item_key, ' and cache ', self.key
                result = f(*args)
                cache.update(item_key, result)
                
            return f(*args)            
        return wrapped_f        
    
    def __get__(self, obj, ownerClass=None):
        return types.MethodType(self, obj)
    