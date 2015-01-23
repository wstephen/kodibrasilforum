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

import threading

class MainLoopThread(threading.Thread):
       
    def __init__(self, main_loop, session):
        threading.Thread.__init__(self)
        self.main_loop = main_loop
        self.session = session
    
    def run(self):
        self.main_loop.loop(self.session)
    
    def stop(self):
        self.main_loop.quit()
        self.join(10)
        self.main_loop = None
        self.session = None