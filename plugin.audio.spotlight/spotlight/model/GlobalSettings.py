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

import xbmcaddon
from spotlight.model.Page import Page

class GlobalSettings:
    
    DisplayTitle, DisplayArtistTitle, DisplayAlbumTitle, DisplayArtistAlbumTitle = 0, 1, 2, 3

    LABEL_TO_TRACK_DISPLAY = {
                        'Title' : DisplayTitle,
                        'Artist - Title': DisplayArtistTitle,
                        'Album - Title': DisplayAlbumTitle,
                        'Artist - Album - Title': DisplayArtistAlbumTitle
    }
    
    ADD_ON_ID = 'plugin.audio.spotlight'
    
    def __init__(self):
        self.refresh_settings()
    
    def refresh_settings(self):
        self.addon = xbmcaddon.Addon(GlobalSettings.ADD_ON_ID)
    
    @property
    def internal_server_port(self):     
        
        return int(self.addon.getSetting('internal_server_port'))
    
    @property
    def override_platform_detection(self):
        
        return self.addon.getSetting('override_platform_detection') == 'true'
    
    @property
    def os(self):
        
        return self.addon.getSetting('os')
    
    @property
    def architecture(self):
        
        return self.addon.getSetting('architecture')   

    @property
    def preferred_track_display(self):
        self.refresh_settings()
        track_display_label = self.addon.getSetting('track_display')
        if not track_display_label.isdigit():
            track_display_label = GlobalSettings.LABEL_TO_TRACK_DISPLAY.get(track_display_label)
            self.addon.setSetting('track_display', str(track_display_label))

        return int(track_display_label)

        '''
        Upper code is just as temporary measure to convert current installs.
        In couple of version this can just be made code below and the LABEL_TO_TRACK_DISPLAY conversion be removed:
        
        self.refresh_settings()

        return int(self.addon.getSetting('track_display'))
        '''
        
    
    def initial_page_for_pagination(self, identifier = ''):
        enable = self.addon.getSetting('enable_pagination') == 'true'
        offset = int(self.addon.getSetting('items_per_page'))
        
        if enable:
            return Page(0, offset, 0, identifier)
        
        return Page.inifinite(identifier)
    
    def initial_page_for_search(self, identifier = ''):
        offset = int(self.addon.getSetting('items_per_page'))
        
        return Page(0, offset, 0, identifier)        
        
    @property    
    def max_playlists_cache_age(self):
        self.refresh_settings()
        
        return int(self.addon.getSetting('max_playlists_cache_age'))
    
    @property
    def enable_playlists_cache(self):
        self.refresh_settings()
        
        return self.addon.getSetting('enable_playlists_cache') == 'true'
        