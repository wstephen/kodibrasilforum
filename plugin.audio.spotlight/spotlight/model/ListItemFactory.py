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

import xbmcgui
from GlobalSettings import GlobalSettings

class ListItemFactory:

    def __init__(self):
        self.settings = GlobalSettings()

    def format_title(self, track_model):
        formatters = {
            GlobalSettings.DisplayTitle: lambda track_model: '%s' % track_model.track,
            GlobalSettings.DisplayAlbumTitle: lambda track_model: '%s - %s' % (track_model.album, track_model.track),
            GlobalSettings.DisplayArtistTitle: lambda track_model: '%s - %s' % (track_model.artist, track_model.track),
            GlobalSettings.DisplayArtistAlbumTitle: lambda track_model: '%s - %s - %s' % (track_model.artist,
                                                                                   track_model.album, track_model.track)
        }
        display_settings = self.settings.preferred_track_display
        formatter = formatters.get(display_settings, lambda track_model: '%s' % track_model.track)

        return formatter(track_model)

    def create_list_item(self, track_model, index=0):
        path = track_model.path
        item = xbmcgui.ListItem(self.format_title(track_model),
                                iconImage=track_model.iconImage,
                                thumbnailImage=track_model.thumbnailImage,
                                path=track_model.path)
        item.setInfo('music', {'album': track_model.album,
                               'artist': track_model.artist,
                               'title': track_model.track,
                               'duration': track_model.time,
                               'tracknumber': index})

        return path, item
    
   
