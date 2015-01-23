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

from spotify import image, link
from spotify.track import TrackAvailability

class UrlGenerator:
    
    def set_session(self, session):
        self.session = session
        
    def set_proxy_info(self, proxy_info):
        self.host = proxy_info.host
        self.port = proxy_info.port
        self.proxy_info = proxy_info
    
    def get_icon_url(self, track):
        ready_track = self.get_playable_if_local(track)
        if ready_track.album() is not None:
            return self.get_image_url(ready_track.album().cover(image.ImageSize.Large))

        return ''

    def get_thumbnail_url(self, track):
        ready_track = self.get_playable_if_local(track)
        if ready_track.album() is not None:
            return self.get_image_url(ready_track.album().cover())

        return ''
        
    def get_playable_if_local(self, track):
        if track.is_local(self.session):
            return track.get_playable(self.session)

        return track
    
    def get_track_url(self, track):
        track_id = self.get_track_id(track)
        headers = self.proxy_info.url_headers
        
        if not track.get_availability(self.session) is TrackAvailability.Available: 
            return ''
        
        return 'http://%s:%s/track/%s.wav|%s' % (self.host, self.port, track_id, headers)
    
    def get_image_url(self, image_id):

        return 'http://%s:%s/image/%s.jpg' % (self.host, self.port, image_id)
    
    def get_track_id(self, track):

        return link.create_from_track(track).as_string()[14:]
    
    def get_album_uri(self, album):
        if album is not None:
            return link.create_from_album(album).as_string()
        
        return ''
    
    def clean_up(self):
        self.session = None
        self.proxy_info = None