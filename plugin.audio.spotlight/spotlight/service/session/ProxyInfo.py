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

from urllib import urlencode

class ProxyInfo:
    
    def __init__(self, proxy_runner):
        self.proxy_runner = proxy_runner
        self.host = proxy_runner.get_host()
        self.port = proxy_runner.get_port()
        self.url_headers = self.get_url_headers()
        
    def get_url_headers(self):
        user_agent = "Spotlight 1.0"
        user_token = self.proxy_runner.get_user_token(user_agent)

        return urlencode({'User-Agent': user_agent, 'X-Spotify-Token': user_token})