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

from spotlight.model.Settings import Settings
from spotify import ConnectionState
import xbmc
import types
import traceback

class SessionGuard(object):
    
    MAX_TRIALS = 2
    
    def __init__ (self, func):
        self.func = func
    
    def __call__ (self, *args, **kw):
        trials = 0
        settings = Settings()
        authenticator = args[0].authenticator
        
        state = authenticator.connection_state()
        while not authenticator.connection_state() is ConnectionState.LoggedIn and trials < SessionGuard.MAX_TRIALS:
            if authenticator.connection_state() == ConnectionState.Offline:
                authenticator.logout()
            state = authenticator.connection_state()
            state = authenticator.login(settings.username, settings.password)
            trials += 1
            
        if authenticator.connection_state() is ConnectionState.LoggedIn:
            try:
                return self.func (*args, **kw)
            except Exception, e:
                xbmc.log('Exception when calling service %s args = %s kw = %s' % (e, args, kw))
                xbmc.log(traceback.format_exc())
                raise Exception('Exception occured. Check logs and report an issue.')
        
        raise Exception("Cannot connect to Spotify. Are your credentials valid?")
    
    def __get__(self, obj, ownerClass=None):
        return types.MethodType(self, obj)
