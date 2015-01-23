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

from spotlight.model.Model import Model
from xmlrpclib import Fault
import xbmcgui
import re
import json
import sys
import urllib
import urlparse
import inspect

class Router:


    def __init__(self, route_config, context = None):
        self.parseArgs()        
        self.path = self.args.get('path', None)        
        self.route_config = route_config
        self.context = context
        
        self.execute()

    def execute_path_function(self, function, args, path):
        try:
            if len(inspect.getargspec(function).args) == 3:
                return getattr(self.context, function.__name__)(args, path)
            else:
                return getattr(self.context, function.__name__)(args)
        except Fault, e:
            dialog = xbmcgui.Dialog()
            message = re.sub(r'<[^>]*>\:', '', e.faultString)
            dialog.ok("Spotlight Error", message)
        except Exception, e:
            dialog = xbmcgui.Dialog()
            dialog.ok("Spotlight Error", str(e))

    def execute(self):
        function = self.route_config.get(self.path)
        args_str = self.args.get('args')
        args = {}
        if args_str != None:
            args = json.loads(args_str)
        if function == None:
            raise Exception("Incorrect router config. No function provided for path = " + self.path)

        if self.context != None:
            self.execute_path_function(function, Model.from_object(args), self.path)            
        else:
            function(args)
        
    @staticmethod    
    def url_for(path, args = {}):
        query = {}
        query['path'] = path
        if not type(args) is dict:
            args = args.__dict__
        query['args'] = json.dumps(args)
        base_url = sys.argv[0]
        for k, v in query.iteritems():
            query[k] = unicode(v).encode('utf-8')
        return base_url + '?' + urllib.urlencode(query)
        
    def parseArgs(self):
        args = urlparse.parse_qs(sys.argv[2][1:])
        for key in args.keys():
            if len(args[key]) == 1:
                args[key] = args[key][0]
        self.args = args
             
        