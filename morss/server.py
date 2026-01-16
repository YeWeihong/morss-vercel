# This file is part of morss
#
# Copyright (C) 2013-2020 pictuga <contact@pictuga.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Server-specific classes for running morss as a standalone HTTP server.

This module is isolated from the WSGI application to prevent Vercel's
serverless runtime from detecting BaseHTTPRequestHandler subclasses.
"""

import wsgiref.simple_server


class WSGIRequestHandlerRequestUri(wsgiref.simple_server.WSGIRequestHandler):
    """
    Custom WSGI request handler that adds REQUEST_URI to the environment.
    
    This is used when running morss as a standalone server with wsgiref.
    It should NOT be imported by the WSGI application or Vercel entry point.
    """
    def get_environ(self):
        env = wsgiref.simple_server.WSGIRequestHandler.get_environ(self)
        env['REQUEST_URI'] = self.path
        return env
