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

from threading import Thread
import xbmc
import time

class ShutdownWatcher(Thread):
       
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server

    def run(self):
        while not xbmc.abortRequested and self.server.server_is_up:
            time.sleep(2)
        
        self.server.stop()
        
        
        
    
    