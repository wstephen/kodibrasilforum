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

from spotlight.service.session.SpotifyCallbacks import SpotifyCallbacks  
from spotlight.service.session.SessionFactory import SessionFactory
from spotlight.service.session.MainLoopThread import MainLoopThread
from spotlight.service.LocalService import LocalService
from spotlight.service.session.Authenticator import Authenticator
from spotlight.service.session.ProxyInfo import ProxyInfo
from spotlight.service.util.UrlGenerator import UrlGenerator
from spotlight.service.util.ModelFactory import ModelFactory
from spotifyproxy.audio import BufferManager
from spotify import MainLoop
from spotify import ConnectionState
from spotifyproxy.httpproxy import ProxyRunner
from SimpleXMLRPCServer import SimpleXMLRPCServer
from spotlight.model.Settings import Settings
from spotlight.service.ShutdownWatcher import ShutdownWatcher
from spotlight.service.CacheStorage import CacheStorage
from spotlight.service.session.PlaylistCallbacks import PlaylistCallbacks


class Server:

    def __init__(self):
        self.settings = Settings()
        self.authenticator = Authenticator()       
        self.url_gen = UrlGenerator()        
        self.model_factory = ModelFactory(self.url_gen)    
        self.session = None    
        self.cache_storage = CacheStorage(self.settings)
        self.server_is_up = False

    def start(self):      
        if not self.server_is_up:              
            self.set_up_session()
            self.runner = self.start_main_loop()        
            self.start_proxy_runner()
            self.set_up_model_factory(self.session, self.proxy_info)
            self.server_is_up = True
            self.install_shutdown_watcher()
        
    def stop(self):
        if self.server_is_up:
            self.session.logout()
            self.runner.stop()
            self.proxy_runner.stop()
            self.server.shutdown()
            self.server.server_close()
            self.clean_up()
            self.server_is_up = False
        
    def is_active(self):
        return self.server_is_up

    def reset_settings(self):
        self.settings = Settings()
    
    def clean_up(self):
        self.session = None
        self.model_factory.clean_up()
        self.proxy_runner = None
        self.proxy_info = None
        self.authenticator.clean_up()
        self.main_loop = None
        self.buffer_manager = None
        self.cache_storage = None
    
    def start_main_loop(self):        
        runner = MainLoopThread(self.main_loop, self.session)
        runner.start()
        return runner

    def start_proxy_runner(self):
        self.proxy_runner = ProxyRunner(self.session, self.buffer_manager, host='127.0.0.1', allow_ranges=False)
        self.proxy_runner.start()
        self.proxy_info = ProxyInfo(self.proxy_runner)
        return self.proxy_info

    def start_rpc_server(self):
        self.server = SimpleXMLRPCServer(("127.0.0.1", self.settings.internal_server_port))
        self.server.register_instance(LocalService(self))        
        self.server.serve_forever()      

    def install_shutdown_watcher(self):
        ShutdownWatcher(self).start()

    def set_up_session(self):
        if self.session is None:
            self.main_loop = MainLoop()
            self.buffer_manager = BufferManager()
            callbacks = SpotifyCallbacks(self, self.main_loop, self.buffer_manager, self.authenticator)
            self.session = SessionFactory(callbacks, self.settings).create_session()
            self.set_up_authenticator(self.session)
            self.authenticator.lastfm_scrobbling(self.settings.lastfm_enabled, self.settings.lastfm_username, self.settings.lastfm_password)

    def set_up_authenticator(self, session):
        self.authenticator.set_session(session)

    def set_up_playlistcontainer_callbacks(self, session):
        container = session.playlistcontainer()
        container.add_callbacks(PlaylistCallbacks(self.cache_storage))
    
    def set_up_model_factory(self, session, proxy_info):
        self.url_gen.set_session(session)
        self.url_gen.set_proxy_info(proxy_info)        

    def log_in(self):
        # Running login twice ends up in offline mode ...
        if self.authenticator.connection_state() == ConnectionState.LoggedIn:
            return

        state = self.authenticator.login(self.settings.username, self.settings.password)
        # TODO This will not be called if the login was performed in SessionGuard
        # if state == ConnectionState.LoggedIn:
        #     self.set_up_playlistcontainer_callbacks(self.session)

    def log_out(self):
        return self.authenticator.logout()

    def get_authenticator(self):
        return self.authenticator
    
    def get_model_factory(self):
        return self.model_factory

    def get_cache_storage(self):
        return self.cache_storage
    
        
