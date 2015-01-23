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

from spotlight.model.GlobalSettings import GlobalSettings
from spotify import Bitrate

import xbmc

class Settings(GlobalSettings):
            
    LABEL_TO_BITRATE = {
                        '96kbps' : Bitrate.Rate96k,
                        '160kbps' :Bitrate.Rate160k,
                        '320kbps' : Bitrate.Rate320k,
                        }
        
    @property        
    def username(self):
        
        return self.addon.getSetting('username')
    
    @property
    def password(self):
        
        return self.addon.getSetting('password')
    
    @property
    def max_cache_size(self):
        
        return int(self.addon.getSetting('max_cache_size'))
    
    @property
    def preferred_bitrate(self):
        bitrate_label = self.addon.getSetting('preferred_bitrate')
        
        xbmc.log('Bitrate label is %s' % bitrate_label)
        
        return Settings.LABEL_TO_BITRATE.get(bitrate_label)
    
    @property
    def volume_normalization(self):
        
        return self.addon.getSetting('volume_normalization')
    
    @property
    def show_missing(self):
        
        return self.addon.getSetting('show_missing') == 'true'

    @property
    def lastfm_enabled(self):
        return self.addon.getSetting('lastfm_enabled') == 'true'

    @property
    def lastfm_username(self):
        return self.addon.getSetting('lastfm_username')

    @property
    def lastfm_password(self):
        return self.addon.getSetting('lastfm_password')
   
