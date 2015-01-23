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
import xbmcgui

class ErrorHandler(object):
    
    def __init__ (self, func):
        self.func = func
    
    def __call__ (self, *args, **kw):
        try:
            return self.func (*args, **kw)
        except Exception, e:
            dialog = xbmcgui.Dialog()
            dialog.ok("SpotiLite Error", str(e))
            

    def __get__(self, obj, ownerClass=None):
        return types.MethodType(self, obj)